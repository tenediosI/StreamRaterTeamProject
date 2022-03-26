import warnings

from django.test import TestCase

import os
import re
import inspect
import tempfile
from stream.models import *
from stream import forms
import stream
from populate_stream import populate
from django.db import models
from django.test import TestCase
from django.conf import settings
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.forms import fields as django_fields

#from StreamRater.stream.models import Category, Streamer

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

f"{FAILURE_HEADER} {FAILURE_FOOTER}"


def create_user_object():
    """
    Helper function to create a User object.
    """
    user = User.objects.get_or_create(username='testuser',
                                      email='test@test.com')[0]
    user.set_password('testabc123')
    user.save()

    return user

def create_super_user_object():
    """
    Helper function to create a super user (admin) account.
    """
    return User.objects.create_superuser('admin', 'admin@test.com', 'testpassword')

def create_category_object():
    """
    Helper function to create a category object
    """
    category = Category.objects.get_or_create(name='testcategory',
                                              image=tempfile.NamedTemporaryFile(suffix=".jpg").name)[0]
    category.save()
    return category

def create_streamer_object():
    """
    Helper function to create a streamer object
    """
    streamer = Streamer.objects.get_or_create(category=create_category_object(),
                                             name='teststreamer',
                                             title='teststreamer',
                                             image=tempfile.NamedTemporaryFile(suffix=".jpg").name,
                                             views='0')[0]
    streamer.save()
    return streamer

def create_comment_object():
    """
    Helper function to create a comment
    """
    comment = Comment.objects.get_or_create(streamer=create_streamer_object(),
                                            user_name='testuser',
                                            rating=3,
                                            text='sample text')[0]
    comment.save()
    return comment

def get_template(path_to_template):
    """
    Helper function to return the string representation of a template file.
    """
    f = open(path_to_template, 'r')
    template_str = ""

    for line in f:
        template_str = f"{template_str}{line}"

    f.close()
    return template_str

class SetupTests(TestCase):
    """
    A simple test to check whether the auth app has been specified.
    """
    def test_installed_apps(self):
        """
        Checks whether the 'django.contrib.auth' app has been included in INSTALLED_APPS.
        """
        self.assertTrue('django.contrib.auth' in settings.INSTALLED_APPS)


class ModelTests(TestCase):
    """
    Tests to check whether the UserProfile model has been created according to the specification.
    """
    def test_userprofile_class(self):
        """
        Does the UserProfile class exist in stream.models? If so, are all the required attributes present?
        Assertion fails if we can't assign values to all the fields required (i.e. one or more missing).
        """
        self.assertTrue('UserProfile' in dir(stream.models))

        user_profile = stream.models.UserProfile()

        # Now check that all the required attributes are present.
        # We do this by building up a UserProfile instance, and saving it.
        expected_attributes = {
            'bio': 'text',
            'picture': tempfile.NamedTemporaryFile(suffix=".jpg").name,
            'user': create_user_object(),
        }

        expected_types = {
            'bio': models.fields.TextField,
            'picture': models.fields.files.ImageField,
            'user': models.fields.related.OneToOneField,
        }

        found_count = 0

        for attr in user_profile._meta.fields:
            attr_name = attr.name

            for expected_attr_name in expected_attributes.keys():
                if expected_attr_name == attr_name:
                    found_count += 1

                    self.assertEqual(type(attr), expected_types[attr_name], f"{FAILURE_HEADER}The type of attribute for '{attr_name}' was '{type(attr)}'; we expected '{expected_types[attr_name]}'. Check your definition of the UserProfile model.{FAILURE_FOOTER}")
                    setattr(user_profile, attr_name, expected_attributes[attr_name])
        
        self.assertEqual(found_count, len(expected_attributes.keys()), f"{FAILURE_HEADER}In the UserProfile model, we found {found_count} attributes, but were expecting {len(expected_attributes.keys())}. Check your implementation and try again.{FAILURE_FOOTER}")
        user_profile.save()
    

    def test_model_admin_interface_inclusion(self):
        """
        Attempts to access the UserProfile admin interface instance.
        If we don't get a HTTP 200, then we assume that the model has not been registered. Fair assumption!
        """
        super_user = create_super_user_object()
        self.client.login(username='admin', password='testpassword')

        # The following URL should be available if the UserProfile model has been registered to the admin interface.
        response = self.client.get('/admin/stream/userprofile/')
        self.assertEqual(response.status_code, 200, f"{FAILURE_HEADER}When attempting to access the UserProfile in the admin interface, we didn't get a HTTP 200 status code. Did you register the new model with the admin interface?{FAILURE_FOOTER}")


class RegisterFormClassTests(TestCase):
    """
    A series of tests to check whether the UserForm and UserProfileForm have been created as per the specification.
    """
    def test_user_form(self):
        """
        Tests whether UserForm is in the correct place, and whether the correct fields have been specified for it.
        """
        self.assertTrue('UserForm' in dir(forms), f"{FAILURE_HEADER}We couldn't find the UserForm class in Stream's forms.py module. Did you create it in the right place?{FAILURE_FOOTER}")
        
        user_form = forms.UserForm()
        self.assertEqual(type(user_form.__dict__['instance']), User, f"{FAILURE_HEADER}Your UserForm does not match up to the User model. Check your Meta definition of UserForm and try again.{FAILURE_FOOTER}")

        fields = user_form.fields
        
        expected_fields = {
            'username': django_fields.CharField,
            'email': django_fields.EmailField,
            'password': django_fields.CharField,
        }
        
        for expected_field_name in expected_fields:
            expected_field = expected_fields[expected_field_name]

            self.assertTrue(expected_field_name in fields.keys(), f"{FAILURE_HEADER}The field {expected_field_name} was not found in the UserForm form. Check you have complied with the specification, and try again.{FAILURE_FOOTER}")
            self.assertEqual(expected_field, type(fields[expected_field_name]), f"{FAILURE_HEADER}The field {expected_field_name} in UserForm was not of the correct type. Expected {expected_field}; got {type(fields[expected_field_name])}.{FAILURE_FOOTER}")
    
    def test_user_profile_form(self):
        """
        Tests whether UserProfileForm is in the correct place, and whether the correct fields have been specified for it.
        """
        self.assertTrue('UserProfileForm' in dir(forms), f"{FAILURE_HEADER}We couldn't find the UserProfileForm class in Rango's forms.py module. Did you create it in the right place?{FAILURE_FOOTER}")
        
        user_profile_form = forms.UserProfileForm()
        self.assertEqual(type(user_profile_form.__dict__['instance']), stream.models.UserProfile, f"{FAILURE_HEADER}Your UserProfileForm does not match up to the UserProfile model. Check your Meta definition of UserProfileForm and try again.{FAILURE_FOOTER}")

        fields = user_profile_form.fields

        expected_fields = {
            'bio': django_fields.CharField,
            'picture': django_fields.ImageField,
        }

        for expected_field_name in expected_fields:
            expected_field = expected_fields[expected_field_name]

            self.assertTrue(expected_field_name in fields.keys(), f"{FAILURE_HEADER}The field {expected_field_name} was not found in the UserProfile form. Check you have complied with the specification, and try again.{FAILURE_FOOTER}")
            self.assertEqual(expected_field, type(fields[expected_field_name]), f"{FAILURE_HEADER}The field {expected_field_name} in UserProfileForm was not of the correct type. Expected {expected_field}; got {type(fields[expected_field_name])}.{FAILURE_FOOTER}")


class RegistrationTests(TestCase):
    """
    A series of tests that examine changes to views.
    Specifically, we look at tests related to registering a user.
    """
    def test_new_registration_view_exists(self):
        """
        Checks to see if the new registration view exists in the correct place, with the correct name.
        """
        url = ''

        try:
            url = reverse('stream:register')
        except:
            pass
        self.assertEqual(url, '/stream//register/', f"{FAILURE_HEADER}Have you created the rango:register URL mapping correctly? It should point to the new register() view, and have a URL of '/stream/register/' Remember the first part of the URL (/stream/) is handled by the project's urls.py module, and the second part (register/) is handled by the Stream app's urls.py module.{FAILURE_FOOTER}")
    
    def test_registration_template(self):
        """
        Does the register.html template exist in the correct place, and does it make use of template inheritance?
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'stream')
        template_path = os.path.join(template_base_path, 'register.html')
        self.assertTrue(os.path.exists(template_path), f"{FAILURE_HEADER}We couldn't find the 'register.html' template in the 'templates/stream/' directory. Did you put it in the right place?{FAILURE_FOOTER}")

        template_str = get_template(template_path)
        full_title_pattern = r'<title>(\s*|\n*)Stream Rater(\s*|\n*)-(\s*|\n*)Register(\s*|\n*)</title>'
        block_title_pattern = r'{% block title_block %}(\s*|\n*)Register(\s*|\n*){% (endblock|endblock title_block) %}'

        request = self.client.get(reverse('stream:register'))
        content = request.content.decode('utf-8')

        self.assertTrue(re.search(full_title_pattern, content), f"{FAILURE_HEADER}The <title> of the response for 'stream:register' is not correct. Check your register.html template, and try again.{FAILURE_FOOTER}")
        self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}Is register.html using template inheritance? Is your <title> block correct?{FAILURE_FOOTER}")

    def test_registration_get_response(self):
        """
        Checks the GET response of the registration view.
        There should be a form with the correct markup.
        """
        request = self.client.get(reverse('stream:register'))
        content = request.content.decode('utf-8')

        self.assertTrue('<h2>Register for Stream Rater</h2>' in content, f"{FAILURE_HEADER}We couldn't find the '<h1>Register for Stream</h1>' header tag in your register template. Did you follow the specification in the book to the letter?{FAILURE_FOOTER}")
        #self.assertTrue('Stream says: <strong>register here!</strong>' in content, f"{FAILURE_HEADER}When loading the register view with a GET request, we didn't see the required 'Rango says: <strong>register here!</strong>'. Check your register.html template and try again.{FAILURE_FOOTER}")
        self.assertTrue('enctype="multipart/form-data"' in content, f"{FAILURE_HEADER}In your register.html template, are you using 'multipart/form-data' for the <form>'s 'enctype'?{FAILURE_FOOTER}")
        self.assertTrue('action="/stream//register/"' in content, f"{FAILURE_HEADER}Is your <form> in register.html pointing to the correct URL for registering a user?{FAILURE_FOOTER}")
        self.assertTrue('<input id="form-submit" type="submit" name="submit" value="Register"/>' in content, f"{FAILURE_HEADER}We couldn't find the markup for the form submission button in register.html. Check it matches what is in the book, and try again.{FAILURE_FOOTER}")
        self.assertTrue('<p><label for="id_password">Password:</label> <input type="password" name="password" placeholder="Make it safe!!" class="form-password" required id="id_password"></p>' in content, f"{FAILURE_HEADER}Checking a random form field in register.html (password), the markup didn't match what we expected. Is your password form field configured correctly?{FAILURE_FOOTER}")
    
    def test_bad_registration_post_response(self):
        """
        Checks the POST response of the registration view.
        What if we submit a blank form?
        """
        request = self.client.post(reverse('stream:register'))
        content = request.content.decode('utf-8')

        self.assertTrue('<ul class="errorlist">' in content)
    
    def test_good_form_creation(self):
        """
        Tests the functionality of the forms.
        Creates a UserProfileForm and UserForm, and attempts to save them.
        Upon completion, we should be able to login with the details supplied.
        """
        user_data = {'username': 'testuser', 'password': 'test123', 'email': 'test@test.com'}
        user_form = forms.UserForm(data=user_data)

        user_profile_data = {'bio': 'sample text', 'picture': tempfile.NamedTemporaryFile(suffix=".jpg").name}
        user_profile_form = forms.UserProfileForm(data=user_profile_data)

        self.assertTrue(user_form.is_valid(), f"{FAILURE_HEADER}The UserForm was not valid after entering the required data. Check your implementation of UserForm, and try again.{FAILURE_FOOTER}")
        self.assertTrue(user_profile_form.is_valid(), f"{FAILURE_HEADER}The UserProfileForm was not valid after entering the required data. Check your implementation of UserProfileForm, and try again.{FAILURE_FOOTER}")

        user_object = user_form.save()
        user_object.set_password(user_data['password'])
        user_object.save()
        
        user_profile_object = user_profile_form.save(commit=False)
        user_profile_object.user = user_object
        user_profile_object.save()
        
        self.assertEqual(len(User.objects.all()), 1, f"{FAILURE_HEADER}We were expecting to see a User object created, but it didn't appear. Check your UserForm implementation, and try again.{FAILURE_FOOTER}")
        self.assertEqual(len(stream.models.UserProfile.objects.all()), 1, f"{FAILURE_HEADER}We were expecting to see a UserProfile object created, but it didn't appear. Check your UserProfileForm implementation, and try again.{FAILURE_FOOTER}")
        self.assertTrue(self.client.login(username='testuser', password='test123'), f"{FAILURE_HEADER}We couldn't log our sample user in during the tests. Please check your implementation of UserForm and UserProfileForm.{FAILURE_FOOTER}")
    
    def test_good_registration_post_response(self):
        """
        Checks the POST response of the registration view.
        We should be able to log a user in with new details after this!
        """
        post_data = {'username': 'webformuser', 'password': 'test123', 'email': 'test@test.com', 'bio': 'sample text', 'picture': tempfile.NamedTemporaryFile(suffix=".jpg").name}
        request = self.client.post(reverse('stream:register'), post_data)
        content = request.content.decode('utf-8')

        self.assertTrue('<h2>Register for Stream Rater</h2>' in content, f"{FAILURE_HEADER}We were missing the '<h1>Register for Rango</h1>' header in the registration response.{FAILURE_FOOTER}")
        self.assertTrue('<a>Registered</a><br>' in content, f"{FAILURE_HEADER}When a successful registration occurs, we couldn't find the expected success message. Check your implementation of register.html, and try again.{FAILURE_FOOTER}")
        self.assertTrue('a id="complete-link" href="/stream/">Return to the homepage.</a><br/>' in content, f"{FAILURE_HEADER}After successfully registering, we couldn't find the expected link back to the Rango homepage.{FAILURE_FOOTER}")

        self.assertTrue(self.client.login(username='webformuser', password='test123'), f"{FAILURE_HEADER}We couldn't log in the user we created using your registration form. Please check your implementation of the register() view. Are you missing a .save() call?{FAILURE_FOOTER}")

    def test_base_for_register_link(self):
        """
        Tests whether the registration link has been added to the base.html template.
        This should work for pre-exercises, and post-exercises.
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'stream')
        base_path = os.path.join(template_base_path, 'base.html')
        template_str = get_template(base_path)
        self.assertTrue('<a href="{% url \'stream:register\' %}">Sign Up</a>' in template_str)
    

class LoginTests(TestCase):
    """
    A series of tests for checking the login functionality of Rango.
    """
    def test_login_url_exists(self):
        """
        Checks to see if the new login view exists in the correct place, with the correct name.
        """
        url = ''

        try:
            url = reverse('stream:login')
        except:
            pass
        
        self.assertEqual(url, '/stream//login/', f"{FAILURE_HEADER}Have you created the stream:login URL mapping correctly? It should point to the new login() view, and have a URL of '/stream/login/' Remember the first part of the URL (/stream/) is handled by the project's urls.py module, and the second part (login/) is handled by the Stream app's urls.py module.{FAILURE_FOOTER}")

    def test_login_functionality(self):
        """
        Tests the login functionality. A user should be able to log in, and should be redirected to the Stream homepage.
        """
        user_object = create_user_object()

        response = self.client.post(reverse('stream:login'), {'username': 'testuser', 'password': 'testabc123'})
        
        try:
            self.assertEqual(user_object.id, int(self.client.session['_auth_user_id']), f"{FAILURE_HEADER}We attempted to log a user in with an ID of {user_object.id}, but instead logged a user in with an ID of {self.client.session['_auth_user_id']}. Please check your login() view.{FAILURE_FOOTER}")
        except KeyError:
            self.assertTrue(False, f"{FAILURE_HEADER}When attempting to log in with your login() view, it didn't seem to log the user in. Please check your login() view implementation, and try again.{FAILURE_FOOTER}")

        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}Testing your login functionality, logging in was successful. However, we expected a redirect; we got a status code of {response.status_code} instead. Check your login() view implementation.{FAILURE_FOOTER}")

    def test_login_template(self):
        """
        Does the login.html template exist in the correct place, and does it make use of template inheritance?
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'stream')
        template_path = os.path.join(template_base_path, 'login.html')
        self.assertTrue(os.path.exists(template_path), f"{FAILURE_HEADER}We couldn't find the 'login.html' template in the 'templates/rango/' directory. Did you put it in the right place?{FAILURE_FOOTER}")

        template_str = get_template(template_path)
        full_title_pattern = r'<title>(\s*|\n*)Stream Rater(\s*|\n*)-(\s*|\n*)Login(\s*|\n*)</title>'
        block_title_pattern = r'{% block title_block %}(\s*|\n*)Login(\s*|\n*){% (endblock|endblock title_block) %}'

        request = self.client.get(reverse('stream:login'))
        content = request.content.decode('utf-8')

        self.assertTrue(re.search(full_title_pattern, content), f"{FAILURE_HEADER}The <title> of the response for 'stream:login' is not correct. Check your login.html template, and try again.{FAILURE_FOOTER}")
        self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}Is login.html using template inheritance? Is your <title> block correct?{FAILURE_FOOTER}")
    
    def test_login_template_content(self):
        """
        Some simple checks for the login.html template. Is the required text present?
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'stream')
        template_path = os.path.join(template_base_path, 'login.html')
        self.assertTrue(os.path.exists(template_path), f"{FAILURE_HEADER}We couldn't find the 'login.html' template in the 'templates/rango/' directory. Did you put it in the right place?{FAILURE_FOOTER}")
        
        template_str = get_template(template_path)
        self.assertTrue('<h2>Please log in</h2>' in template_str, f"{FAILURE_HEADER}We couldn't find the '<h1>Login to Rango</h1>' in the login.html template.{FAILURE_FOOTER}")
        self.assertTrue('<button id="form-submit" type="submit"value="Submit">' in template_str, f"{FAILURE_HEADER}We couldn't find the submit button in your login.html template. .{FAILURE_FOOTER}")
    
    def test_navbar_greeting(self):
        """
        Checks to see if the navbar changes to show my account when a user logs in.
        """
        content = self.client.get(reverse('stream:homepage')).content.decode()
        self.assertTrue('Login' in content, f"{FAILURE_HEADER}We didn't see the generic greeting for a user not logged in on the Stream homepage. Please check your homepage.html template.{FAILURE_FOOTER}")

        create_user_object()
        self.client.login(username='testuser', password='testabc123')
        
        content = self.client.get(reverse('stream:homepage')).content.decode()
        self.assertTrue('My Account' in content, f"{FAILURE_HEADER}After logging a user, we didn't see the expected message welcoming them on the homepage. Check your index.html template.{FAILURE_FOOTER}")

class StaticMediaTests(TestCase):
    """
    A series of tests to check whether static files and media files have been setup and used correctly.
    Also tests for the two required files -- images.jpg and NoProfile.jpg.
    """

    def setUp(self):
        self.project_base_dir = os.getcwd()
        self.static_dir = os.path.join(self.project_base_dir, 'static')
        self.media_dir = os.path.join(self.project_base_dir, 'media')

    def test_does_static_directory_exist(self):
        """
        Tests whether the static directory exists in the correct location -- and the images subdirectory.
        Also checks for the presence of images.jpeg and NoProfile.jpg in the images subdirectory.
        """
        does_static_dir_exist = os.path.isdir(self.static_dir)
        does_images_static_dir_exist = os.path.isdir(os.path.join(self.static_dir, 'images'))
        does_NoProfile_jpg_exist = os.path.isfile(os.path.join(self.static_dir, 'images', 'NoProfile.jpg'))
        does_images_jpeg_exist = os.path.isfile(os.path.join(self.static_dir, 'images', 'images.jpeg'))

        self.assertTrue(does_static_dir_exist,
                        f"{FAILURE_HEADER}The static directory was not found in the expected location. Check the instructions in the book, and try again.{FAILURE_FOOTER}")
        self.assertTrue(does_images_static_dir_exist,
                        f"{FAILURE_HEADER}The images subdirectory was not found in your static directory.{FAILURE_FOOTER}")
        self.assertTrue(does_NoProfile_jpg_exist,
                        f"{FAILURE_HEADER}We couldn't locate the NoProfile.jpg image in the /static/images/ directory. If you think you've included the file, make sure to check the file extension. Sometimes, a JPG can have the extension .jpeg. Be careful! It must be .jpg for this test.{FAILURE_FOOTER}")
        self.assertTrue(does_images_jpeg_exist,
                        f"{FAILURE_HEADER}We couldn't locate the images.jpeg image in the /static/images/ directory. If you think you've included the file, make sure to check the file extension. Sometimes, a JPG can have the extension .jpeg. Be careful! It must be .jpg for this test.{FAILURE_FOOTER}")

    def test_does_media_directory_exist(self):
        """
        Tests whether the media directory exists in the correct location.
        """
        does_media_dir_exist = os.path.isdir(self.media_dir)

        self.assertTrue(does_media_dir_exist,
                        f"{FAILURE_HEADER}We couldn't find the /media/ directory in the expected location. Make sure it is in your project directory (at the same level as the manage.py module).{FAILURE_FOOTER}")

    def test_static_and_media_configuration(self):
        """
        Performs a number of tests on your Django project's settings in relation to static files and user upload-able files..
        """
        static_dir_exists = 'STATIC_DIR' in dir(settings)
        self.assertTrue(static_dir_exists,
                        f"{FAILURE_HEADER}Your settings.py module does not have the variable STATIC_DIR defined.{FAILURE_FOOTER}")

        expected_path = os.path.normpath(self.static_dir)
        static_path = os.path.normpath(settings.STATIC_DIR)
        self.assertEqual(expected_path, static_path,
                         f"{FAILURE_HEADER}The value of STATIC_DIR does not equal the expected path. It should point to your project root, with 'static' appended to the end of that.{FAILURE_FOOTER}")

        staticfiles_dirs_exists = 'STATICFILES_DIRS' in dir(settings)
        self.assertTrue(staticfiles_dirs_exists,
                        f"{FAILURE_HEADER}The required setting STATICFILES_DIRS is not present in your project's settings.py module. Check your settings carefully. So many students have mistyped this one.{FAILURE_FOOTER}")
        self.assertEqual([static_path], settings.STATICFILES_DIRS,
                         f"{FAILURE_HEADER}Your STATICFILES_DIRS setting does not match what is expected. Check your implementation against the instructions provided.{FAILURE_FOOTER}")

        staticfiles_dirs_exists = 'STATIC_URL' in dir(settings)
        self.assertTrue(staticfiles_dirs_exists,
                        f"{FAILURE_HEADER}The STATIC_URL variable has not been defined in settings.py.{FAILURE_FOOTER}")
        self.assertEqual('/static/', settings.STATIC_URL,
                         f"{FAILURE_HEADER}STATIC_URL does not meet the expected value of /static/. Make sure you have a slash at the end!{FAILURE_FOOTER}")

        media_dir_exists = 'MEDIA_DIR' in dir(settings)
        self.assertTrue(media_dir_exists,
                        f"{FAILURE_HEADER}The MEDIA_DIR variable in settings.py has not been defined.{FAILURE_FOOTER}")

        expected_path = os.path.normpath(self.media_dir)
        media_path = os.path.normpath(settings.MEDIA_DIR)
        self.assertEqual(expected_path, media_path,
                         f"{FAILURE_HEADER}The MEDIA_DIR setting does not point to the correct path. Remember, it should have an absolute reference to tango_with_django_project/media/.{FAILURE_FOOTER}")

        media_root_exists = 'MEDIA_ROOT' in dir(settings)
        self.assertTrue(media_root_exists,
                        f"{FAILURE_HEADER}The MEDIA_ROOT setting has not been defined.{FAILURE_FOOTER}")

        media_root_path = os.path.normpath(settings.MEDIA_ROOT)
        self.assertEqual(media_path, media_root_path,
                         f"{FAILURE_HEADER}The value of MEDIA_ROOT does not equal the value of MEDIA_DIR.{FAILURE_FOOTER}")

        media_url_exists = 'MEDIA_URL' in dir(settings)
        self.assertTrue(media_url_exists,
                        f"{FAILURE_HEADER}The setting MEDIA_URL has not been defined in settings.py.{FAILURE_FOOTER}")

        media_url_value = settings.MEDIA_URL
        self.assertEqual('/media/', media_url_value,
                         f"{FAILURE_HEADER}Your value of the MEDIA_URL setting does not equal /media/. Check your settings!{FAILURE_FOOTER}")

    def test_context_processor_addition(self):
        """
        Checks to see whether the media context_processor has been added to your project's settings module.
        """
        context_processors_list = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        self.assertTrue('django.template.context_processors.media' in context_processors_list,
                        f"{FAILURE_HEADER}The 'django.template.context_processors.media' context processor was not included. Check your settings.py module.{FAILURE_FOOTER}")


class LogoutTests(TestCase):
    """
    A few tests to check the functionality of logging out. Does it work? Does it actually log you out?
    """
    def test_bad_request(self):
        """
        Attempts to log out a user who is not logged in.
        This should  redirect you to the login page.
        """
        response = self.client.get(reverse('stream:logout'))
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, reverse('stream:login'))
    
    def test_good_request(self):
        """
        Attempts to log out a user who is logged in.
        This should succeed -- we should be able to login, check that they are logged in, logout, and perform the same check.
        """
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')

        try:
            self.assertEqual(user_object.id, int(self.client.session['_auth_user_id']), f"{FAILURE_HEADER}We attempted to log a user in with an ID of {user_object.id}, but instead logged a user in with an ID of {self.client.session['_auth_user_id']}. Please check your login() view. This happened when testing logout functionality.{FAILURE_FOOTER}")
        except KeyError:
            self.assertTrue(False, f"{FAILURE_HEADER}When attempting to log a user in, it failed. Please check your login() view and try again.{FAILURE_FOOTER}")
        
        # Now lot the user out. This should cause a redirect to the homepage.
        response = self.client.get(reverse('stream:logout'))
        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}Logging out a user should cause a redirect, but this failed to happen. Please check your logout() view.{FAILURE_FOOTER}")
        self.assertTrue('_auth_user_id' not in self.client.session, f"{FAILURE_HEADER}Logging out with your logout() view didn't actually log the user out! Please check yout logout() view.{FAILURE_FOOTER}")


class LinkTidyingTests(TestCase):
    """
    Some checks to see whether the links in base.html have been tidied up and change depending on whether a user is logged in or not.
    We don't check for category/page links here; these are done in the exercises.
    """
    def test_omnipresent_links(self):
        """
        Checks for links that should always be present, regardless of user state.
        """
        content = self.client.get(reverse('stream:homepage')).content.decode()
        self.assertTrue('href="/stream//about/"' in content)
        self.assertTrue('href="/stream/"' in content)

        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')

        # These should be present.
        content = self.client.get(reverse('stream:homepage')).content.decode()
        self.assertTrue('href="/stream//about/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/stream/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
    
    def test_logged_in_links(self):
        """
        Checks for links that should only be displayed when the user is logged in.
        """
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        content = self.client.get(reverse('stream:homepage')).content.decode()

        # These should be present.
        self.assertTrue('href="/stream//testuser/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/stream//logout/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")

        # These should not be present.
        self.assertTrue('href="/stream//login/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/stream//register/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
    
    def test_logged_out_links(self):
        """
        Checks for links that should only be displayed when the user is not logged in.
        """
        content = self.client.get(reverse('stream:homepage')).content.decode()

        # These should be present.
        self.assertTrue('href="/stream//login/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/stream//register/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        
        # These should not be present.
        self.assertTrue('href="/stream//testuser/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/stream//logout/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")

class ProfilePages(TestCase):
    """
    Checks that profile pages work as desired
    """
    def test_profile_template_exists(self):
        """
        Checks whether the profile related html templates exists.
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'stream')
        template_view_path = os.path.join(template_base_path, 'view_profile.html')
        template_edit_path = os.path.join(template_base_path, 'edit_profile.html')
        self.assertTrue(os.path.exists(template_view_path), f"{FAILURE_HEADER}We couldn't find the 'view_profile.html' template in the 'templates/stream/' directory. Did you put it in the right place? {FAILURE_FOOTER}")
        self.assertTrue(os.path.exists(template_edit_path), f"{FAILURE_HEADER}We couldn't find the 'edit_profile.html' template in the 'templates/stream/' directory. Did you put it in the right place? {FAILURE_FOOTER}")


    def test_profile_template_inherits(self):
        """
        Checks for template inheritance in profile related html's
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'stream')
        template_view_path = os.path.join(template_base_path, 'view_profile.html')
        template_edit_path = os.path.join(template_base_path, 'edit_profile.html')

        template_str = get_template(template_view_path)
        block_title_pattern = r"{% block title_block %}(\s*|\n*){{ user.username }}'s profile(\s*|\n*){% (endblock|endblock title_block) %}"

        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        request = self.client.get(reverse('stream:view_profile', kwargs={'username': 'testuser'}))
        content = request.content.decode('utf-8')

        self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}Is view_profile.html using template inheritance? Is your <title> block correct?{FAILURE_FOOTER}")

        template_str = get_template(template_edit_path)
        block_title_pattern = r'{% block title_block %}(\s*|\n*)Edit Profile(\s*|\n*){% (endblock|endblock title_block) %}'

        self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}Is edit_profile.html using template inheritance? Is your <title> block correct?{FAILURE_FOOTER}")

class CommentPages(TestCase):
    """
    Checks that comment pages work
    """
    def test_streamer_page(self):
        create_comment_object()

        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'stream')
        template_streamer_path = os.path.join(template_base_path, 'streamer.html')

        template_str = get_template(template_streamer_path)
        full_title_pattern = r'<title>(\s*|\n*)Stream Rater(\s*|\n*)-(\s*|\n*)teststreamer(\s*|\n*)</title>'

        request = self.client.get(reverse('stream:show_streamer', kwargs={'name': 'teststreamer',
                                                                          'category_name_slug': 'testcategory'}))
        content = request.content.decode('utf-8')

        self.assertTrue(re.search(full_title_pattern, content),
                        f"{FAILURE_HEADER}The <title> of the response for 'stream:show_streamer' is not correct. Check your streamer.html template, and try again.{FAILURE_FOOTER}")

        self.assertTrue('<h1 id="streamer-name">teststreamer</h1>' in content, f"{FAILURE_HEADER}We are missing the streamer name header in the streamer response.{FAILURE_FOOTER}")
        self.assertTrue('Category: <a>testcategory</a>' in content, f"{FAILURE_HEADER}We are missing category name{FAILURE_FOOTER}")
        self.assertTrue('Views this month: <a>0</a>' in content, f"{FAILURE_HEADER}We are missing monthly views{FAILURE_FOOTER}")
        self.assertTrue('Rating: <a>3.0</a>' in content, f"{FAILURE_HEADER}We are missing rating{FAILURE_FOOTER}")
        self.assertTrue('<div class="comment-header"><a class="user-name" href="/stream//testuser/">testuser</a><a class="date">    March 25, 2022</a><br/>' in content, f"{FAILURE_HEADER}Missing test comment{FAILURE_FOOTER}")

    def test_streamer_page_logged_in(self):
        create_streamer_object()

        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')

        request = self.client.get(reverse('stream:show_streamer', kwargs={'name': 'teststreamer',
                                                                          'category_name_slug': 'testcategory'}))
        content = request.content.decode('utf-8')

        self.assertTrue('<a class="button" id="make-review" href="/stream/testcategory/teststreamer/comment/">Add A Review</a>' in content, f"{FAILURE_HEADER}We are missing make review button{FAILURE_FOOTER}")

    def test_streamer_page_logged_out(self):
        create_streamer_object()

        request = self.client.get(reverse('stream:show_streamer', kwargs={'name': 'teststreamer',
                                                                          'category_name_slug': 'testcategory'}))
        content = request.content.decode('utf-8')
        self.assertTrue('<p>You are not registered to make comments</p>' in content, f"{FAILURE_HEADER}We are missing make review denial message{FAILURE_FOOTER}")

    def test_add_review(self):
        create_streamer_object()
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')

        request = self.client.get(reverse('stream:add_comment', kwargs={'name': 'teststreamer',
                                                                          'category_name_slug': 'testcategory'}))
        content = request.content.decode('utf-8')
        self.assertTrue('<textarea name="text" cols="100" rows="20" class="form-bio" style="height: 5em;" id="id_text">' in content,
                        f"{FAILURE_HEADER}We are missing text area input{FAILURE_FOOTER}")
        self.assertTrue('<p>Give us your opinion:</p>' in content,
                        f"{FAILURE_HEADER}We are missing text area input header{FAILURE_FOOTER}")
        self.assertTrue('<input type="number" name="rating" value="0" required id="id_rating">' in content,
                        f"{FAILURE_HEADER}We are missing make rating input{FAILURE_FOOTER}")
        self.assertTrue('Rating between 1-5' in content,
                        f"{FAILURE_HEADER}We are missing rating input header{FAILURE_FOOTER}")
        self.assertTrue('<input class="button" id="post-comment" type="submit" name="submit" value="post comment" />' in content,
                        f"{FAILURE_HEADER}We are missing submission button{FAILURE_FOOTER}")

class DatabaseConfigurationTests(TestCase):
    """
    These tests should pass if you haven't tinkered with the database configuration.
    N.B. Some of the configuration values we could check are overridden by the testing framework -- so we leave them.
    """

    def setUp(self):
        pass

    def does_gitignore_include_database(self, path):
        """
        Takes the path to a .gitignore file, and checks to see whether the db.sqlite3 database is present in that file.
        """
        f = open(path, 'r')

        for line in f:
            line = line.strip()

            if line.startswith('db.sqlite3'):
                return True

        f.close()
        return False

    def test_databases_variable_exists(self):
        """
        Does the DATABASES settings variable exist, and does it have a default configuration?
        """
        self.assertTrue(settings.DATABASES,
                        f"{FAILURE_HEADER}Your project's settings module does not have a DATABASES variable, which is required. Check the start of Chapter 5.{FAILURE_FOOTER}")
        self.assertTrue('default' in settings.DATABASES,
                        f"{FAILURE_HEADER}You do not have a 'default' database configuration in your project's DATABASES configuration variable. Check the start of Chapter 5.{FAILURE_FOOTER}")

    def test_gitignore_for_database(self):
        """
        If you are using a Git repository and have set up a .gitignore, checks to see whether the database is present in that file.
        """
        git_base_dir = os.popen('git rev-parse --show-toplevel').read().strip()

        if git_base_dir.startswith('fatal'):
            warnings.warn(
                "You don't appear to be using a Git repository for your codebase. Although not strictly required, it's *highly recommended*. Skipping this test.")
        else:
            gitignore_path = os.path.join(git_base_dir, '.gitignore')

            if os.path.exists(gitignore_path):
                self.assertTrue(self.does_gitignore_include_database(gitignore_path),
                                f"{FAILURE_HEADER}Your .gitignore file does not include 'db.sqlite3' -- you should exclude the database binary file from all commits to your Git repository.{FAILURE_FOOTER}")
            else:
                warnings.warn(
                    "You don't appear to have a .gitignore file in place in your repository. We ask that you consider this! Read the Don't git push your Database paragraph in Chapter 5.")

class AdminInterfaceTests(TestCase):
    """
    A series of tests that examines the authentication functionality (for superuser creation and logging in), and admin interface changes.
    Have all the admin interface tweaks been applied, and have the two models been added to the admin app?
    """

    def setUp(self):
        """
        Create a superuser account for use in testing.
        Logs the superuser in, too!
        """
        User.objects.create_superuser('testAdmin', 'email@email.com', 'adminPassword123')
        self.client.login(username='testAdmin', password='adminPassword123')

        create_comment_object()

    def test_admin_interface_accessible(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200,
                         f"{FAILURE_HEADER}The admin interface is not accessible. Check that you didn't delete the 'admin/' URL pattern in your project's urls.py module.{FAILURE_FOOTER}")

    def test_models_present(self):
        """
        Checks whether the two models are present within the admin interface homepage -- and whether Stream is listed there at all.
        """
        response = self.client.get('/admin/')
        response_body = response.content.decode()

        # Is the Stream app present in the admin interface's homepage?
        self.assertTrue('Models in the Stream application' in response_body,
                        f"{FAILURE_HEADER}The Stream app wasn't listed on the admin interface's homepage. You haven't added the models to the admin interface.{FAILURE_FOOTER}")

        # Check each model is present.
        self.assertTrue('Categories' in response_body,
                        f"{FAILURE_HEADER}The Category model was not found in the admin interface. If you did add the model to admin.py, did you add the correct plural spelling (Categories)?{FAILURE_FOOTER}")
        self.assertTrue('Streamers' in response_body,
                        f"{FAILURE_HEADER}The Page model was not found in the admin interface. If you did add the model to admin.py, did you add the correct plural spelling (Streamers)?{FAILURE_FOOTER}")
        self.assertTrue('Comments' in response_body,
                        f"{FAILURE_HEADER}The Comment model was not found in the admin interface. If you did add the model to admin.py, did you add the correct plural spelling (Comments)?{FAILURE_FOOTER}")
        self.assertTrue('Sub_Comments' in response_body,
                        f"{FAILURE_HEADER}The Sub_Comment model was not found in the admin interface. If you did add the model to admin.py, did you add the correct plural spelling (Sub_Comments)?{FAILURE_FOOTER}")

    def test_comment_display_changes(self):
        """
        Checks to see whether the Page model has had the required changes applied for presentation in the admin interface.
        """
        response = self.client.get('/admin/stream/comment/')
        response_body = response.content.decode()

        # Headers -- are they all present?
        self.assertTrue('<div class="text"><a href="?o=1">ID</a></div>' in response_body,
                        f"{FAILURE_HEADER}ID column not present in admin{FAILURE_FOOTER}")
        self.assertTrue('<div class="text"><a href="?o=2">User name</a></div>' in response_body,
                        f"{FAILURE_HEADER}User name column not present in admin{FAILURE_FOOTER}")
        self.assertTrue('<div class="text"><a href="?o=3">Date</a></div>' in response_body,
                        f"{FAILURE_HEADER}Date column not present in admin{FAILURE_FOOTER}")

        # Is the teststreamer page present, and in order?
        expected_str = '<tr class="row1"><td class="action-checkbox"><input type="checkbox" name="_selected_action" value="1" class="action-select"></td><th class="field-id"><a href="/admin/stream/comment/1/change/">1</a></th><td class="field-user_name">testuser</td><td class="field-date nowrap">March 25, 2022</td></tr>'
        self.assertTrue(expected_str in response_body,
                        f"{FAILURE_HEADER}Couldn't find generated streamer listed{FAILURE_FOOTER}")

    def test_streamer_display_changes(self):
        """
        Checks to see whether the Page model has had the required changes applied for presentation in the admin interface.
        """
        response = self.client.get('/admin/stream/streamer/')
        response_body = response.content.decode()

        # Headers -- are they all present?
        self.assertTrue('<div class="text"><a href="?o=1">Name</a></div>' in response_body,
                        f"{FAILURE_HEADER}Name column not present in admin{FAILURE_FOOTER}")
        self.assertTrue('<div class="text"><a href="?o=2">Category</a></div>' in response_body,
                        f"{FAILURE_HEADER}Category column not present in admin{FAILURE_FOOTER}")
        self.assertTrue('<div class="text"><a href="?o=3">Rating</a></div>' in response_body,
                        f"{FAILURE_HEADER}Rating column not present in admin{FAILURE_FOOTER}")

        # Is the teststreamer page present, and in order?
        expected_str = '<tr class="row1"><td class="action-checkbox"><input type="checkbox" name="_selected_action" value="1" class="action-select"></td><th class="field-name"><a href="/admin/stream/streamer/1/change/">teststreamer</a></th><td class="field-category nowrap">testcategory</td><td class="field-rating">0.0</td></tr>'
        self.assertTrue(expected_str in response_body,
                        f"{FAILURE_HEADER}Couldn't find generated streamer listed{FAILURE_FOOTER}")