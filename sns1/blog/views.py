from django.shortcuts import render, get_object_or_404, redirect

from django.views import generic

from .models import Post, Category, Comment, Reply

from django.http import Http404, JsonResponse, HttpResponseBadRequest

from django.utils import timezone

from django.db.models import Q

from django.core.mail import EmailMessage

from django.template.loader import render_to_string

from django.conf import settings

from django.core.signing import BadSignature, SignatureExpired, loads, dumps

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.http import require_POST

from .forms import PostSearchForm, CommentCreateForm, ReplyCreateForm

import json
# Create your views here.





class ArchiveListMixin:

    model = Post

    pagenate_by = 12

    date_field = 'create_at'

    template_name ='blog/post_list.html'

    allow_empty = True

    make_object_list = True





class PostList(ArchiveListMixin, generic.ArchiveIndexView):



    def get_queryset(self):

        return super().get_queryset().select_related('category')



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['heading'] = '最近の日記'

        return context





class PostDetail(generic.DetailView):

    model = Post



    def get_object(self, queryset=None):

        post = super().get_object()

        if post.created_at <= timezone.now():

            return post

        raise Http404





class PostCategoryList(ArchiveListMixin, generic.ArchiveIndexView):



    def get_queryset(self):

        self.category = category = get_object_or_404(Category, pk=self.kwargs['pk'])

        return super().get_queryset().filter(category=category).select_related('category')



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['heading'] = '[{}] カテゴリの日記'.format(self.category.name)

        return context


class PostYearList(ArchiveListMixin, generic.YearArchiveView):

    def get_queryset(self):
        return super().get_queryset().select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotext['heading'] = '{}年の日記'.format(self.kwargs['year'])
        return context


class PostMonthList(ArchiveListMixin, generic.MonthArchiveView):
    month_format = '%m'

    def get_queryset(self):
        return super().get_queryset().select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = '{}年{}月の日記'.format(self.kwargs['year'], self.kwargs['month'])


class PostSearchList(ArchiveListMixin, generic.ArchiveIndexView):

    def get_queryset(self):
        queryset = super().get_queryset()
        self.request.form = form = PostSearchForm(self.request.GET)
        form.is_valid()
        self.key_word = key_word = form.cleaned_data['key_word']
        if key_word:
            queryset = queryset.filter(Q(title__icontains=key_word) | Q(text__icontains=key_word))
        return queryset.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotext['heading'] = '[{}]　の検索結果'.format(self.key_word)
        return context


class CommentCreate(generic.CreateView):
    model = Comment
    form_class = CommentCreateForm

    def form_valid(self, form):
        post_pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_pk)
        comment = form.save(commit=False)
        comment.target = post
        comment.request = self.request
        comment.save()
        return redirect('blog:detail', pk=post.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context


class ReplyCreate(generic.CreateView):
    model = Reply
    form_class = ReplyCreateForm
    template_name = 'blog/comment_form.html'

    def form_valid(self, form):
        comment_pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        reply = form.save(commit=False)
        reply.target = comment
        reply.request = self.request
        reply.save()
        return redirect('blog:detail', pk=comment.target.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        context['post'] = comment.target
        return context


@require_POST
def subscribe_email(request):
    form = EMailForm(request.POST)

    if form.is_valid():
        push = form.save()
        context = {
            'token': dumps(push.pk),
        }
        subject = render_to_string('blog/mail/confirm_push_subject.txt', context, request)
        message = render_to_string('blog/mail/confirm_push_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [push.mail]
        bcc = [settings.DEFAULT_FROM_EMAIL]
        email = EmailMessage(subject, message, from_email, to, bcc)
        email.send()
        return JsonResponse({'message': 'Thanks!! メールに、登録用のURLを送付しました。'})

    return JsonResponse(form.errors.get_json_data(), status=400)


def subscribe_email_register(request, token):
    try:
        user_pk = loads(token, max_age=60*60*24)

    except SignatureExpired:
        return HttpResponseBadRequest()

    except BadSignature:
        return HttpResponseBadRequest()

    else:
        try:
            push = EmailPush.objects.get(pk=user_pk)
        except EmailPush.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            if not push.is_active:
                push.is_active = True
                push.save()
                return redirect('blog:subscribe_email_done')

    return HttpResponseBadRequest()


def subscribe_email_done(request):
    return render(request, 'blog/subscribe_email_done.html')
