from django.db.models import Q
from django.views import generic
from pybb.models import Post, Topic

class Search(generic.ListView):
    template_name = 'search/search.html'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.query = request.GET.get('q')
        return super(Search, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Post.objects.all()
        if not self.query:
            return qs.none()
        for word in self.query.split()[:10]:
            qs = qs.filter(Q(body_text__icontains=word) |
                           Q(topic__name__icontains=word))
        topic_list = qs.values_list('topic', flat=True)
        return Topic.objects.filter(pk__in=topic_list)

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)
        context['query'] = self.query
        return context