from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import EmailPostForm, CommentForm, SearchForm
from django.contrib.postgres.search import TrigramSimilarity


def post_list(request, tag_slug=None):
	object_list = Post.published.all()
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])

	paginator = Paginator(object_list, 3) # 3 posts in each page
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, return the first page
		posts = paginator.page(1)
	except EmptyPage:
		# If page is out of range, return the last page
		posts = paginator.page(paginator.num_pages)
	return render( request,
				'blog/post/list.html',
				{'page': page,
				'posts': posts,
				'tag': tag
				})
	#return render(request, 'blog/post/list.html', {'posts': posts})
	

# Create your views here.
def post_detail(request, year, month, day, slug_post):
	from .models import Post, Comment
	from .forms import EmailPostForm, CommentForm

	post = get_object_or_404(Post, slug=slug_post, status='published', publish__year=year, publish__month=month, publish__day=day)

	comments = post.comments.filter(active=True) #List of active comments for this post

	new_comment = None
	if request.method == 'POST':
		# A comment was posted
		comment_form = CommentForm(data=request.POST)
		if comment_form.is_valid():
			new_comment = comment_form.save(commit=False) # Create Comment object but don't save to DB yet
			new_comment.post = post # Assign the current post to the comment
			new_comment.save() # Save the comment to the database
	else:
		comment_form = CommentForm()
	post_tags_ids = post.tags.values_list('id', flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

	return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form, 'similar_posts': similar_posts})

def post_share(request, post_id):
	# Retrieve post by id
	post = get_object_or_404(Post, id=post_id, status='published')
	sent = False

	if request.method == 'POST':
		# Form was submitted
		form = EmailPostForm(request.POST)
		if form.is_valid():
			# Form fields passed validation
			cd = form.cleaned_data
			# ... send email
			post_url = request.build_absolute_uri(post.get_absolute_url())
			subject = f"{cd['name']} recommends you read {post.title}"
			message = f"Read {post.title} at {post_url}\n\n" \
					  f"{cd['name']}\'s comments: {cd['comments']}\n" \
					  f"They can be reached at {cd['email']}"
			send_mail(subject, message, '21fall.cps242@gmail.com ', [cd['to']])
			sent = True
	else:
		form = EmailPostForm()
	return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent':sent})

def post_search(request):
	form = SearchForm()
	query = None
	results = []
	if 'query' in request.GET:
		form = SearchForm(request.GET)
		if form.is_valid():
			query = form.cleaned_data['query']
			search_vector = SearchVector('title', weight='A') + \
							SearchVector('body', weight='B')
			search_query = SearchQuery(query)
			results = Post.published.annotate(
				similarity=TrigramSimilarity('title', query),
				).filter(similarity__gt=0.1).order_by('-similarity')
	return render(request, 'blog/post/search.html',
					{'form': form,
					'query': query,
					'results': results})