#!/usr/bin/env python
# -*- coding: utf-8 -*-  
from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView

from app.models import Album, AlbumImage

def gallery(request):
    list = Album.objects.filter(is_visible=True).order_by('-created')
    paginator = Paginator(list, 10)

    page = request.GET.get('page')
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        albums = paginator.page(1) # If page is not an integer, deliver first page.
    except EmptyPage:
        albums = paginator.page(paginator.num_pages) # If page is out of range (e.g.  9999), deliver last page of results.

    return render(request, 'gallery.html', { 'albums': list })

class AlbumDetail(DetailView):
     model = Album

     def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AlbumDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the images
        context['images'] = AlbumImage.objects.filter(album=self.object.id)
        return context

def handler404(request, exception):
    assert isinstance(request, HttpRequest)
    return render(request, 'handler404.html', None, None, 404)

import mimetypes
from django.http import HttpResponse
import os
from zipfile import ZipFile
import tempfile
def download_file(request, slug):
    # fill these variables with real values
    #s=Album.objects.get(slug=slug)

    fl_path_base = "/home/biltzevoy/hochzeit/django-photo-gallery/django_photo_gallery/media/albums/"

    # get all fotos
    files = os.listdir(fl_path_base)
    final_files = []
    final_files_paths = []

    for f in files:
        if f.startswith(f"{slug}-"):
            final_files.append(f)
            final_files_paths.append(os.path.join(fl_path_base, f))

    response = HttpResponse(content_type='application/zip')
    with tempfile.NamedTemporaryFile() as tmp:
        # writing files to a zipfile
        with ZipFile(tmp.name, 'w') as zipf:
            # writing each file one by one
            for p, f in zip(final_files_paths, final_files):
                zipf.write(p, f)
        with open(tmp.name,'rb') as zipf:
            response = HttpResponse(zipf, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={slug}.zip'
    return response
