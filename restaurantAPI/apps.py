from django.apps import AppConfig


class RestaurantapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurantAPI'

    def ready(self):
        import restaurantAPI.signals
