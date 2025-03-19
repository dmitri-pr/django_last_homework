from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView

from newblogapp.models import Article


class ArticleListView(ListView):
    queryset = (
        Article.objects
        .filter(published_at__isnull=False)
        .order_by('-published_at')
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = 'Latest blog articles'
    description = 'Updates on changes and addition of blog articles'
    link = reverse_lazy('newblogapp:articles')

    def items(self):
        return (
            (
                Article.objects
                .filter(published_at__isnull=False)
                .order_by('-published_at')[:5]
            )
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]

    # def item_link(self, item: Article):
    #     return reverse(
    #         'newblogapp:article', kwargs={'pk': item.pk}
    #     )

