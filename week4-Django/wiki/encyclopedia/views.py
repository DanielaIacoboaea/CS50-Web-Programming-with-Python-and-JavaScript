from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django import forms
from django.urls import reverse
import markdown

from django.core.exceptions import ValidationError
from numpy import random

from . import util

class SearchForm(forms.Form):
    q = forms.CharField(label="Search Article", widget=forms.TextInput(attrs={'class': 'search'}))

class AddNewEntryForm(forms.Form):
    title = forms.CharField(label="Title", 
        widget=forms.TextInput(attrs={'class': 'add-title', 'placeholder': 'New title'}))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        'placeholder': 'Type in the body for your new entry in Markdown format'}))
    def clean(self):
        title = self.cleaned_data['title']
        if title.casefold() in [article.casefold() for article in util.list_entries()]:
            raise ValidationError("Invalid title")


# use hidden field to send the title 
# from content display page to edit page 
class hiddenTitle(forms.Form):
    editTitle = forms.CharField(widget = forms.HiddenInput(), required = False)


class editEntry(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'add-title'}))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'textarea-edit'}))
    def clean(self):
        testTitle = self.cleaned_data['title']
        if testTitle not in util.list_entries():
            raise ValidationError("Can't uptate, title does not exist.")



def index(request):
    """
    List the names of all pages in the encyclopedia.
    The user can click on any entry name to be taken
    directly to that entry page.
    """

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })



def entry(request, title):
    """
    Displays the contents of an encyclopedia entry.
    If an entry is requested that does not exist, 
    show an error page indicating that their requested page was not found.
    """

    get_titles = util.list_entries()
    found = False
    for idx, entry in enumerate(get_titles):
        if title.casefold() == entry.casefold():
            found = True
            entry_index = idx
            break

    if found:
        content = util.get_entry(get_titles[entry_index])
        form = hiddenTitle(initial={'editTitle': get_titles[entry_index]})
        return render(request, "encyclopedia/entry.html", {
            "title": get_titles[entry_index],
            "content": markdown.markdown(content),
            "form": form
        })
    else:
        return HttpResponseNotFound("The requested page was not found.")


def search(request):
    """
    Redirect to encyclopedia entries list that are either fully matched
    or have the search query as a substring.
    """

    if request.method == "POST":
        substringTitles = []
        form = SearchForm(request.POST)
        if form.is_valid():
            searchTitle = form.cleaned_data['q']
            if searchTitle.casefold() in [title.casefold() for title in util.list_entries()]:
                return HttpResponseRedirect(reverse("entry", kwargs={'title':searchTitle}))
            else:
                for title in util.list_entries():
                    if searchTitle in title:
                        substringTitles.append(title)
                if not substringTitles:
                    return HttpResponseNotFound("The requested page was not found.")
                else:
                    return render(request, "encyclopedia/index.html", {
                        "entries": substringTitles,
                        "form": SearchForm()
                    })
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })


def addNew(request):
    """
    Create a new encyclopedia entry using Markdown content.
    If an encyclopedia entry already exists with the provided title,
    show error message.
    """

    if request.method == 'POST':
        addForm = AddNewEntryForm(request.POST)
        if addForm.is_valid():
            newTitle = addForm.cleaned_data['title']
            content = addForm.cleaned_data['content']
            util.save_entry(newTitle, content)
            return HttpResponseRedirect(reverse("entry", kwargs={'title':newTitle}))
        else:
            return render(request, "encyclopedia/new_page.html", {
            'title': "Create New Page",
            "addForm": addForm
            })

    return render(request, "encyclopedia/new_page.html", {
        'title': "Create New Page",
        "addForm": AddNewEntryForm()
    })


def edit(request):
    """
    Redirect to edit Markdown content for an entry.
    Use hidden field from display contents to 
    pre-populated with the existing Markdown content of the page.
    """

    if request.method == 'POST':
        form = hiddenTitle(request.POST)
        if form.is_valid():
            title = form.cleaned_data['editTitle']
            if title in util.list_entries():
                content = util.get_entry(title)
                editForm = editEntry()
                editForm.fields['title'].initial = title
                editForm.fields['content'].initial = content
                return render(request, "encyclopedia/edit-page.html", {
                    'title': "Edit Page",
                    "editForm": editForm
                })
        else:
            return HttpResponseRedirect(reverse("entry", kwargs={'title':title}))


def saveEdit(request):
    """
    Save the changes made to the entry.
    """

    if request.method == 'POST':
        editForm = editEntry(request.POST)
        if editForm.is_valid():
            newTitle = editForm.cleaned_data['title']
            content = editForm.cleaned_data['content']
            if newTitle in util.list_entries() and content:
                util.save_entry(newTitle, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'title':newTitle}))
        else:
            return render(request, "encyclopedia/edit-page.html", {
                    'title': "Edit Page",
                    "editForm": editForm
                })


def randomEntry(request):
    """
    Generate a random encyclopedia entry.
    """

    if request.method == "GET":
        entries = util.list_entries()
        index = random.randint(len(entries))
        return HttpResponseRedirect(reverse("entry", kwargs={'title':entries[index]}))
