from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


# APP:ID_OF_URL_IN_APP
RECIPES_URL = reverse('recipe:recipe-list')

# Helper Functions


def detail_url(recipe_id):
    """Return recipe detail URL"""
    # /api/recipe/recipes
    # /api/recipe/recipes/1/
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):  # arguments to dictionary pass **params
    """Create and return a sample recipe"""
    # default fields setup pass params to dic and dic to params below
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    # overrides **params dictionary keys or if don't exist create
    defaults.update(params)

    # convert dictionary "default to arguments"
    return Recipe.objects.create(user=user, **defaults)
    # reverse effect when calling func conversion vs when passing params


# Per Class Unique Test same file
# Class as big container function lifeCycle begin end
# mem locations garbage collection


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        # Create2recipes without store them somewhere(no access direct)justInDB
        # and retrieve them below from db by id (for same user 2 recipes)
        sample_recipe(user=self.user)
        # sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        # data as a list return/pass below
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'password123'
        )
        # Create2User recipes without store them somewhere(no access direct)
        # not shared recipes read docstring above
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        # No API inconsistent needs list not object one
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        # add many to many this way
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        # single object not list view
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
