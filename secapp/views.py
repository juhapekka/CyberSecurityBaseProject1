from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Note


@login_required
def index(request):
    notes = Note.objects.filter(owner=request.user)
    return render(request, 'secapp/index.html', {'notes': notes})


# NOTE CREATION
@login_required
def add_note(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Note.objects.create(owner=request.user, content=content)
    return redirect('/')

# FLAW 1: Broken Access Control (A01:2021)
@login_required
def view_note(request, note_id):
    # FLAW: read note directly using ID without checking ownership
    note = Note.objects.get(id=note_id)
    
    # FIX: check note is owned by registered user
    # note = Note.objects.get(id=note_id, owner=request.user)
    
    return render(request, 'secapp/note.html', {'note': note})


# FLAW 2: Injection (A03:2021)
@login_required
def search_notes(request):
    query = request.GET.get('q', '')
    
    # FLAW: raw SQL-query
    cursor = connection.cursor()
    cursor.execute(f"SELECT content FROM secapp_note WHERE content LIKE '%{query}%'")
    results = cursor.fetchall()
    
    # FIX: Use Django ORM api to do safe query
    # results = Note.objects.filter(owner=request.user, content__icontains=query)
    
    return render(request, 'secapp/search.html', {'results': results, 'query': query})


# FLAW 3: CSRF (allowed exploit)
# FLAW: disable CSRF check in critical functionality
@csrf_exempt
@login_required
def delete_note(request, note_id):
    # FIX: remove @csrf_exempt decorator from above
    if request.method == 'POST':
        Note.objects.filter(id=note_id, owner=request.user).delete()
    return redirect('/')

# FLAW 4: Identification and Authentication Failures (A07:2021)
@csrf_exempt
def custom_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # FLAW: compare passwords in plaintext / not using authenticate api from Django
        # Here get user and check without proper hashing
        user = User.objects.filter(username=u).first()
        if user and user.check_password(p): # FLAW (part 2): no protection against brute force or db limitations
            login(request, user)
            return redirect('/')
            
        # FIX: Use authenticate() api from Django and limit attempts
        # from django.contrib.auth import authenticate
        # user = authenticate(request, username=u, password=p)
        # if user is not None:
        #     login(request, user)
        #     return redirect('/')

    return render(request, 'secapp/login.html')