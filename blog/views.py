from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Commentaire, Tag
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def liste_articles(request):
    articles = Article.objects.all().order_by('-date_publication')
    return render(request, 'blog/liste_articles.html', {'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    commentaires = article.commentaire_set.all().order_by('-date') # type: ignore
    tags = article.tags.all()
    return render(request, 'blog/single_article.html', {
        'article': article,
        'commentaires': commentaires,
        'tags': tags,
    })

@login_required
def ajouter_commentaire(request, slug):
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        article = get_object_or_404(Article, slug=slug)
        Commentaire.objects.create(article=article, utilisateur=request.user, contenu=contenu)
    return redirect('article_detail', slug=slug)

@login_required
def like_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    if user in article.likes.all():
        article.likes.remove(user) # type: ignore
        liked = False
    else:
        article.likes.add(user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': article.likes.count()})
