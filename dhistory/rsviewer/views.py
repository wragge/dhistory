# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.core.cache import cache
from bs4 import BeautifulSoup
import mechanize
import urllib2
import httplib2
import re
import os
from urllib2 import Request, urlopen, URLError, HTTPError
from cStringIO import StringIO
import Image as pil
import math

from django.conf import settings
from django.http import Http404

CACHE_TIMEOUT = 60 * 60

def show_naa_home(request):
    return render_to_response('rsviewer-home.html', {}, context_instance=RequestContext(request))

def show_naa_page(request, barcode, page=1):
    page = int(page)
    details = cache.get('%s-details' % barcode)
    if details is None:
        details = get_item_details(barcode)
        cache.set('%s-details' % barcode, details, CACHE_TIMEOUT)
    total = cache.get('%s-pages' % barcode)
    if total is None:
        total = get_total_pages(barcode)
        cache.set('%s-pages' % barcode, total, CACHE_TIMEOUT)
    next = page + 1 if page < total else None
    previous = page - 1 if page > 1 else None
    return render_to_response('rsviewer-item.html', {'page': page, 'barcode': barcode, 'details': details, 'total': total, 'next': next, 'previous': previous }, context_instance=RequestContext(request))

def show_wall(request, barcode):
    page = int(request.GET.get('page', 1))
    count = int(request.GET.get('count', 40))
    total = cache.get('%s-pages' % barcode)
    if total is None:
        total = get_total_pages(barcode)
        cache.set('%s-pages' % barcode, total, CACHE_TIMEOUT)
    pages = math.ceil(float(total)/count)
    if (pages > pages):
        raise Http404
    else:
        start = ((page - 1) * count) + 1
        end = (total + 1) if total < (start + count) else (start + count)
        images = []
        details = cache.get('%s-details' % barcode)
        if details is None:
            details = get_item_details(barcode)
            cache.set('%s-details' % barcode, details, CACHE_TIMEOUT)
        for image in range(start, end):
            images.append(image)
            #images.append('/archives/naa/images/%s/%s/?width=200&height=200' % (barcode, image))
        return render_to_response('rsviewer-wall.html', {'images': images, 'details': details, 'page': page + 1, 'barcode': barcode, 'total': total}, context_instance=RequestContext(request))

def show_printing(request, barcode):
    pages = request.GET.get('pages', None)
    details = cache.get('%s-details' % barcode)
    if details is None:
        details = get_item_details(barcode)
        cache.set('%s-details' % barcode, details, CACHE_TIMEOUT)
    total = cache.get('%s-pages' % barcode)
    if total is None:
        total = get_total_pages(barcode)
        cache.set('%s-pages' % barcode, total, CACHE_TIMEOUT)
    if pages:
        ranges = pages.split(',')
    else:
        ranges = ['1-%s' % total]
    print_pages = []
    for rng in ranges:
        if '-' in rng:
            start, end = rng.split('-')
            for page_num in range(int(start), int(end) + 1):
                print_pages.append(page_num)
        else:
            print_pages.append(range)
    return render_to_response('rsviewer-print.html', {'pages': print_pages, 'details': details, 'barcode': barcode, 'total': total}, context_instance=RequestContext(request))
        
def get_total_pages(barcode):
    url = 'http://recordsearch.naa.gov.au/scripts/Imagine.asp?B=%s&I=1&SE=1' % barcode
    print url
    response = get_url(url)
    soup = BeautifulSoup(response.read())
    try:
        num_pages = soup.find('input', id='Hidden3')['value']
    except TypeError:
        raise Http404
    print num_pages
    return int(num_pages)

def get_item_details(barcode):
    br = mechanize.Browser()
    br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]
    br.set_handle_robots(False)
    url = 'http://www.naa.gov.au/cgi-bin/Search?O=I&Number=%s' % barcode
    response1 = br.open(url)
    # Recordsearch returns a page with a form that submits on page load.
    # Have to make sure the session id is submitted with the form.
    # Extract the session id.
    session_id = re.search(r"value={(.*)}", response1.read()).group(1)
    br.select_form(name="t")
    br.form.set_all_readonly(False)
    # Add session id to the form.
    br.form['NAASessionID'] = '{%s}' % session_id
    response2 = br.submit()
    soup = BeautifulSoup(response2.read())
    try:
        series = unicode(soup.find('div', text='Series number').parent.next_sibling.next_sibling.a.string)
        control = unicode(soup.find('div', text='Control symbol').parent.next_sibling.next_sibling.string)
        title = unicode(soup.find('div', text='Title').parent.next_sibling.next_sibling.string)
    except AttributeError:
        raise Http404
    return {'series': series, 'control': control, 'title': title}

def get_naa_image(request, barcode, page):
    width = request.GET.get('width', '')
    height = request.GET.get('height', '')
    source_filename = get_naa_image_source(barcode, page)
    source_filepath = os.path.join(settings.MEDIA_ROOT, 'archives/naa/%s' % source_filename)
    if width or height:
        deriv_filename = '%s-%s-%sx%s.jpg' % (barcode, page, width, height)
        deriv_filepath = os.path.join(settings.MEDIA_ROOT, 'archives/naa/%s' % deriv_filename)
        if not os.path.exists(deriv_filepath):
            width = int(width) if width else 2000
            height = int(height) if height else 2000
            with open(source_filepath, 'rb') as f:
                content = f.read()
            deriv = rescale(content, width, height, force=False)
            with open(deriv_filepath, 'wb') as f:
                f.write(deriv)
        filename = deriv_filename
    else:
        filename = source_filename
    print filename
    return redirect('%sarchives/naa/%s' % (settings.MEDIA_URL, filename))

def get_naa_image_source(barcode, page):
    filename = '%s-%s.jpg' % (barcode, page)
    filepath = os.path.join(settings.MEDIA_ROOT, 'archives/naa/%s' % filename)
    if not os.path.exists(filepath):
        h = httplib2.Http()
        url = 'http://naa16.naa.gov.au/rs_images/ShowImage.php?B=%s&S=%s&T=R' % (barcode, page)
        try:
            resp, content = h.request(url, "GET")
            with open(filepath, 'wb') as f:
                f.write(content)
        except:
            raise Http404
    return filename
   
def get_url(url):
    '''
    Retrieve page.
    '''
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    try:
        response = opener.open(url)
    except HTTPError, error:
        if error.code >= 500:
            raise ServerError(error)
        else:
            raise
    except URLError, error:
        raise
    else:
        return response

class ServerError(Exception):
    pass

def rescale(data, width, height, force=True):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""
    from cStringIO import StringIO
    
    max_width = width
    max_height = height

    input_file = StringIO(data)
    img = pil.open(input_file)
    if not force:
        img.thumbnail((max_width, max_height), pil.ANTIALIAS)
    else:
        src_width, src_height = img.size
        src_ratio = float(src_width) / float(src_height)
        dst_width, dst_height = max_width, max_height
        dst_ratio = float(dst_width) / float(dst_height)
        
        if dst_ratio < src_ratio:
            crop_height = src_height
            crop_width = crop_height * dst_ratio
            x_offset = float(src_width - crop_width) / 2
            y_offset = 0
        else:
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            #y_offset = float(src_height - crop_height) / 3
            y_offset = 0
        img = img.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
        img = img.resize((dst_width, dst_height), pil.ANTIALIAS)
        
    tmp = StringIO()
    img.save(tmp, 'JPEG')
    tmp.seek(0)
    output_data = tmp.getvalue()
    input_file.close()
    tmp.close()
    
    return output_data