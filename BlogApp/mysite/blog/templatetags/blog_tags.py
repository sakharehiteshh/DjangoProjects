from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag
def total_posts():
	return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
	latest_posts = Post.published.order_by('-publish')[:count]
	return {'latest_posts': latest_posts}

@register.simple_tag
def get_Leaderboard(count=3):
	return User.objects.annotate(author_Posts=Count('blog_posts')).order_by('-author_Posts')[:count]

@register.simple_tag
def get_most_commented_posts(count=5):
	return Post.published.annotate(
			total_comments=Count('comments')
			).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text):
	return mark_safe(markdown.markdown(text))

