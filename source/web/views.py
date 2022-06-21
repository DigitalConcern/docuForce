from django.contrib import messages
from django.forms import TextInput
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import asyncio
from sesame import utils
from . import models
from . import forms
from .forms import ProgramForm, UserForm, FAQForm
from django.utils.translation import gettext as _


class HomePageView(TemplateView):
    template_name = 'home.html'


class UsersPageView(TemplateView):
    model = models.ActiveUsers
    template_name = 'users.html'

    # fields = ['user_id', 'code_name']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = models.ActiveUsers.objects.all()
        return context


# class ProgramsPageView(TemplateView):
#     model = models.Programs
#     template_name = 'programs.html'
#     # form_class = forms.CommentForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['programs'] = models.Programs.objects.all()
#         return context


class ProgramsPageView(TemplateView):
    model = models.Programs
    template_name = "programs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = models.Programs.objects.all()
        return context


class CreateProgView(CreateView):
    model = models.Programs
    template_name = "programs/create.html"
    fields = ['name', 'description', 'info', 'faq', 'category', 'is_active', 'link']

    # data = {'form': ProgramForm()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProgramForm
        return context

    def form_valid(self, form):
        elem = models.Programs()
        elem.key = len(
            models.Programs.objects.filter(category=form.cleaned_data["category"]).values_list("id", flat=True)) + 1
        elem.name = form.cleaned_data["name"]
        prg_name = elem.name
        elem.link = form.cleaned_data["link"]
        elem.description = form.cleaned_data["description"]
        elem.info = form.cleaned_data["info"]
        elem.faq = form.cleaned_data["faq"]
        elem.is_active = form.cleaned_data["is_active"]
        elem.category = form.cleaned_data["category"]
        elem.save()
        messages.info(self.request, _("Программа " + prg_name + " успешно сохранена!"))
        return redirect("/programs")

    def get_success_url(self) -> str:
        print("done")
        return render(self, 'programs/create.html')
    # def create(self):
    #     form = ProgramForm()
    #     data = {'form': form}
    #     return render(self, 'programs/create.html')


class ProgramsEditView(UpdateView):
    model = models.Programs
    template_name = "programs/create.html"
    form_class = ProgramForm

    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)
    #
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        elem = models.Programs()
        elem.id = self.object.id
        elem.key = len(models.Programs.objects.filter(category=form.cleaned_data["category"])) + 1
        elem.name = form.cleaned_data["name"]
        prg_name = elem.name
        elem.faq = form.cleaned_data["faq"]
        elem.link = form.cleaned_data["link"]
        elem.description = form.cleaned_data["description"]
        elem.info = form.cleaned_data["info"]
        elem.is_active = form.cleaned_data["is_active"]
        elem.category = form.cleaned_data["category"]

        elem.save()
        i = 1
        for elem in models.Programs.objects.filter(category="school"):
            elem.key = i
            i += 1
            elem.save()
        i = 1
        for elem in models.Programs.objects.filter(category="students"):
            elem.key = i
            i += 1
            elem.save()
        messages.info(self.request, _("Программа " + prg_name + " успешно изменена!"))
        return redirect("/programs")

        # fields = ['id', 'key', 'name', 'description']
    # widgets = {
    #     "id": TextInput(attrs={'class': 'form-control', 'placeholder': 'ID'}),
    #     "key": TextInput(attrs={'class': 'form-control', 'placeholder': 'key'}),
    #     "name": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
    #     "description": TextInput(attrs={'class': 'form-control', 'placeholder': 'Краткое описание'})
    # }


class ProgramsDeleteView(DeleteView):
    model = models.Programs
    template_name = "programs/delete.html"
    success_url = "/programs"

    def form_valid(self, form):
        self.object = self.get_object()
        old_category = self.object.category
        prg_name = self.object.name
        success_url = self.get_success_url()
        self.object.delete()
        i = 1
        for elem in models.Programs.objects.filter(category=old_category):
            elem.key = i
            i += 1
            elem.save()
        messages.info(self.request, _("Программа " + prg_name + " успешно удалена!"))
        return HttpResponseRedirect(success_url)


class UsersEditView(UpdateView):
    model = models.ActiveUsers
    template_name = "users_edit.html"
    form_class = UserForm

    def form_valid(self, form):
        elem = models.ActiveUsers()
        elem.user_id = form.cleaned_data["user_id"]
        elem.code_name = form.cleaned_data["code_name"]
        elem.user_name = form.cleaned_data["user_name"]
        elem.grade = form.cleaned_data["grade"]
        elem.is_admin = form.cleaned_data["is_admin"]
        if form.cleaned_data["is_admin"] is True:
            user = models.ActiveUsers.objects.get(user_id=int(elem.user_id))
            login_token = utils.get_parameters(user)
            elem.link = "http://178.216.98.48/?sesame={}".format(login_token["sesame"])
            print(elem.link)
        elem.save()
        return redirect("/users")


class UsersDelView(DeleteView):
    model = models.ActiveUsers
    template_name = "users_delete.html"
    success_url = "/users"


class FAQView(UpdateView):
    model = models.FAQ
    template_name = "faq.html"
    form_class = FAQForm

    def form_valid(self, form):
        elem = models.FAQ()
        elem.id = 1
        elem.text = form.cleaned_data["text"]
        elem.save()
        return redirect("/faq/1")
