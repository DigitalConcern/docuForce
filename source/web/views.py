from django.contrib import messages
from django.forms import TextInput
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import asyncio
from . import models
from . import forms
from django.utils.translation import gettext as _


class HomePageView(TemplateView):
    template_name = 'home.html'
