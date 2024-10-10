# views.py
from django.shortcuts import render, redirect, get_object_or_404
# in
from .models import Vote, Option, VoteHistory
from .forms import VoteForm, OptionForm, VoteAccessForm
# ex
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib import messages

# user auth
def user_logout(request):
    logout(request)
    return redirect('vote_list')  # or any other page you want to redirect to after logout

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                user.save()
                return redirect('user_login')  # Redirect to login page after successful registration
            else:
                error_message = "Username already exists"
        else:
            error_message = "Passwords do not match"

        return render(request, 'form_register.html', {'error': error_message})

    return render(request, 'form_register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')  # Redirect to Django admin page
            else:
                return redirect('vote_list')  # Redirect to vote list page for regular users
        else:
            return render(request, 'form_login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'form_login.html')

# for user --------------------------------------------------------------------------------------

# fungsi untuk menampilkan halaman awal 
@csrf_exempt
def get_started(request):
    return render(request, 'get_started.html')

# fungsi untuk menampilkan list vote dan menampilkan detail vote
@csrf_exempt
def vote_list(request):
    votes = Vote.objects.all().order_by('-id')
    return render(request, 'vote_list.html', {'votes': votes})

# Fungsi untuk menyimpan status suka dan tidak suka setiap vote
@login_required
@csrf_exempt
def like_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    
    if vote.likes.filter(id=request.user.id).exists():
        # Jika user sudah like, maka hapus like (unlike)
        vote.likes.remove(request.user)
    else:
        # Jika user belum like, tambahkan like
        vote.likes.add(request.user)

    return redirect('vote_list')

# fungsi untuk membuat vote baru dan menambahkan option ke dalamnya 
@login_required
@csrf_exempt 
def create_vote(request):
    if request.method == 'POST':
        vote_form = VoteForm(request.POST)
        if vote_form.is_valid():
            # Simpan vote tanpa commit dulu agar kita bisa menambahkan user dan deadline
            vote = vote_form.save(commit=False)
            
            # Set user yang sedang login sebagai pembuat vote
            vote.created_by = request.user
            
            # Ambil waktu dari form dan ubah ke timezone-aware
            deadline_input = request.POST.get('deadline')
            if deadline_input:
                # Parsing input menjadi datetime dan mengubahnya menjadi aware
                deadline = parse_datetime(deadline_input)
                vote.deadline = timezone.make_aware(deadline, timezone.get_current_timezone())

            vote.save()  # Simpan vote ke database

            return redirect('add_options', vote_id=vote.id)  # Redirect ke halaman untuk menambahkan opsi
    else:
        vote_form = VoteForm()

    return render(request, 'form_vote.html', {'vote_form': vote_form})

# fungsi untuk menambahkan option ke dalam vote yang ada yang dibuat sebelumnya 
@login_required
@csrf_exempt
def add_options(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    options = vote.options.count()
    if request.method == 'POST':
        option_form = OptionForm(request.POST)
        if option_form.is_valid():
            option = option_form.save(commit=False)
            option.vote = vote
            option.save()
            return redirect('add_options', vote_id=vote.id)
    else:
        option_form = OptionForm()
    return render(request, 'form_option.html', {'vote': vote, 'option_form': option_form, 'options': options})

# fungsi untuk mengakses vote dengan kunci yang diberikan oleh user 
@login_required
@csrf_exempt
def access_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    if request.method == 'POST':
        form = VoteAccessForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            if key == vote.key:
                request.session[f'vote_{vote.id}_access'] = True 
                return redirect('vote_detail', vote_id=vote.id)
            else:
                form.add_error('key', 'Kunci Tidak Valid!')
    else:
        form = VoteAccessForm()
    return render(request, 'access_vote.html', {'form': form, 'vote': vote})

# fungsi untuk menampilkan detail vote dengan kunci yang diberikan oleh user 
@login_required
@csrf_exempt
def vote_detail(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    history = VoteHistory.objects.filter(vote=vote)

    # Cek total vote
    total_votes = vote.total_votes()

    local_now = timezone.localtime()
    print('waktu', local_now)

    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(Option, id=option_id)

        # Cek apakah user sudah pernah melakukan vote
        user_vote_history = VoteHistory.objects.filter(user=request.user, vote=vote).first()

        if user_vote_history:
            if user_vote_history.option == option:
                return redirect('vote_detail', vote_id=vote.id)

            previous_option = user_vote_history.option
            previous_option.votes -= 1
            previous_option.save()

            user_vote_history.option = option
            user_vote_history.save()
        else:
            VoteHistory.objects.create(user=request.user, vote=vote, option=option)

        option.votes += 1
        option.save()

        return redirect('vote_detail', vote_id=vote.id)

    return render(request, 'vote_detail.html', {
        'vote': vote, 
        'total_votes': total_votes, 
        'history': history,
        'local_now': local_now,
    })

# for admin --------------------------------------------------------------------------------------
@csrf_exempt
def admin_vote_list(request):
    user = request.user
    votes = Vote.objects.filter(created_by=user)  # Filter vote berdasarkan user yang login
    return render(request, 'admin_vote.html', {'votes': votes})

@login_required
def edit_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id, created_by=request.user)
    
    if request.method == 'POST':
        vote_form = VoteForm(request.POST, instance=vote)
        if vote_form.is_valid():
            vote = vote_form.save(commit=False)
            # Mengubah deadline jika diubah oleh user
            deadline_input = request.POST.get('deadline')
            if deadline_input:
                deadline = parse_datetime(deadline_input)
                vote.deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
            vote.save()
            return redirect('admin_vote_list')  
    else:
        vote_form = VoteForm(instance=vote)

    return render(request, 'form_vote_edit.html', {'vote_form': vote_form})

@login_required
def delete_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id, created_by=request.user)
    
    if request.method == 'GET':
        vote.delete()
        messages.success(request, "Vote berhasil dihapus.")
        return redirect('admin_vote_list')

def admin_vote_option(request):
    votes = Vote.objects.all().order_by('-id')
    return render(request, 'admin_vote_option.html', {'votes': votes})
