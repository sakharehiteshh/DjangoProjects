from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
	object_list = Post.published.all()
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
				}
				)
	#return render(request, 'blog/post/list.html', {'posts': posts})
	

# Create your views here.
def post_detail(request, year, month, day, slug_post):
	post = get_object_or_404(Post, slug=slug_post, status='published', publish__year=year, publish__month=month, publish__day=day)
	return render(request, 'blog/post/detail.html', {'post': post})