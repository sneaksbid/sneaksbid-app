from django.urls import reverse_lazy
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView
from sneaksbid.models import Item, Bid, OrderItem
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from snekasbiddjangoProject import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from .tokens import generate_token
from decimal import Decimal
from django.conf import settings
from .forms import SignUpForm, ShoeForm
from .forms import SignInForm,CheckoutForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PaymentForm, BidForm
from .models import Payment, Shoe,Order,BillingAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .models import Item
from django.db.models import F
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect


'''class HomeView(ListView):
    template_name = "./sneaksbid/homepage.html"
    context_object_name = 'items'
    ordering = ['-bid_expiry']

    def get_queryset(self):
        return Item.objects.all()'''

class HomeView(ListView):
    template_name = "./sneaksbid/homepage.html"
    context_object_name = 'items'
    ordering = ['-bid_expiry']

    def get_queryset(self):
        return Item.objects.all()

    def dispatch(self, request, *args, **kwargs):
        # Initialize or increment the visit count in the session
        if 'visit_count' in request.session:
            request.session['visit_count'] += 1
        else:
            request.session['visit_count'] = 1

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include visit count in the context
        context['visit_count'] = self.request.session['visit_count']
        return context
    

def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pass1 = form.cleaned_data['pass1']

            user = authenticate(username=username, password=pass1)
            if user is not None:
                login(request, user)
                fname = user.first_name
                # messages.success(request, "Logged In Successfully!!")
                return render(request, "authentication/index.html", {"fname": fname})
            else:
                messages.error(request, "Bad Credentials!!")
                return redirect('home')
    else:
        form = SignInForm()
    return render(request, "authentication/signin_1.html", {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists! Please try some other username.")
                return redirect('home')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email Already Registered!!")
                return redirect('home')

            if password1 != password2:
                messages.error(request, "Passwords didn't match!!")
                return redirect('home')

            user = form.save(commit=False)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False  # Change to `True` if you don't need email confirmation
            user.save()

            # Send welcome email
            subject = "Welcome to SneaksBid Login!!"
            message = "Hello " + user.first_name + "!! \n" + "Welcome to SneaksBid!! \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You\n"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            # Send email confirmation
            current_site = get_current_site(request)
            email_subject = "Confirm your Email @ SneaksBid Login!!"
            message2 = render_to_string('email_confirmation.html', {
                'name': user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.fail_silently = True
            email.send()

            messages.success(request,
                             "Your Account has been created successfully! Please check your email to confirm your email address in order to activate your account.")
            return redirect('signin')
        else:
            # Form is not valid
            messages.error(request, "Error processing your form.")
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup_1.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')


def shop(request):
    # Retrieve all items from the database
    sneakers = Item.objects.all()

    context = {
        'sneakers': sneakers,
    }

    return render(request, 'sneaksbid/shop.html', context)


def search_sneakers(request):
    query = request.GET.get('query')
    search_results = Item.objects.filter(title__icontains=query)
    return render(request, 'sneaksbid/search_result.html', {'search_results': search_results})


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'sneaksbid/item_detail.html', {'item': item})


@login_required
def place_bid(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if not item.available:
        messages.error(request, "The item is not available.")
        return redirect('item_detail', item_id=item.id)

    if request.method == 'POST':
        form = BidForm(request.POST, item=item)
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']
            last_bid = item.bids.order_by('-bid_amount').first()
            if last_bid and bid_amount <= last_bid.bid_amount:
                messages.error(request, "Your bid must be higher than the current highest bid.")
                return redirect('place_bid', item_id=item.id)
            elif bid_amount <= item.base_price:
                messages.error(request, "Your bid must be higher than the base price.")
                return redirect('place_bid', item_id=item.id)

            bid = form.save(commit=False)
            bid.item = item
            bid.user = request.user
            bid.save()
            messages.success(request, "Bid placed successfully.")

            return redirect('item_detail', item_id=item.id)
        else:
            messages.error(request, "There was a problem with your bid.")
    else:
        form = BidForm(item=item)

    user_won_auction = False
    if not item.is_auction_active:
        highest_bid = item.bids.order_by('-bid_amount').first()
        if highest_bid and highest_bid.user == request.user:
            user_won_auction = True

    return render(request, 'sneaksbid/bid.html', {'form': form, 'item': item, 'user_won_auction': user_won_auction})


from .models import Bid

class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve winning bid details for the current user
        winning_bids = Bid.objects.filter(user=request.user, is_winner=True)
        
        # Pass bid details to the template for rendering the checkout form
        context = {'winning_bids': winning_bids}
        return render(request, 'sneaksbid/checkout.html', context)

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Process the form data and save it to the database
            billing_address = BillingAddress(
                user=request.user,
                street_address=form.cleaned_data.get('street_address'),
                apartment_address=form.cleaned_data.get('apartment_address'),
                country=form.cleaned_data.get('country'),
                zip_code=form.cleaned_data.get('zip'),
                same_shipping_address=form.cleaned_data.get('same_shipping_address'),
                save_info=form.cleaned_data.get('save_info'),
                payment_option=form.cleaned_data.get('payment_option')
            )
            billing_address.save()

            # Redirect to a different URL upon successful checkout
            return HttpResponseRedirect(reverse('home'))

        # If form is not valid, render the checkout form again with error messages
        context = {'form': form}
        return render(request, 'sneaksbid/checkout.html', context)
    

def process_payment(request, client_secret):
    if request.method == "POST":
        stripe.api_key = settings.STRIPE_PRIVATE_KEY
        intent = stripe.PaymentIntent.confirm(client_secret)

        if intent.status == 'succeeded':
            # Update the Payment model
            payment_id = intent.metadata['payment_id']
            payment = Payment.objects.get(id=payment_id)
            payment.paid = True
            payment.save()

            messages.success(request, 'Payment successful!')
            return redirect('home')

    context = {'client_secret': client_secret}
    return render(request, './sneaksbid/process_payment.html', context)


class ShoeCreateView(LoginRequiredMixin, CreateView):
    model = Shoe
    form_class = ShoeForm
    template_name = 'sneaksbid/shoe_form.html'  # Adjust the template path if needed
    success_url = reverse_lazy('home')
    login_url = '/signin/'


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileImageForm
from .models import Profile


@login_required
def dashboard(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        image_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and image_form.is_valid():
            user_form.save()
            image_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        image_form = ProfileImageForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'image_form': image_form
    }

    return render(request, 'sneaksbid/dashboard.html', context)
