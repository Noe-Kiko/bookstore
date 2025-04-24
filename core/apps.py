from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        This runs when Django starts - perfect place to ensure categories and images exist
        """
        # Only run this in production (Azure)
        if os.environ.get('WEBSITE_HOSTNAME'):
            # Import here to avoid AppRegistryNotReady error
            from django.contrib.auth import get_user_model
            from .models import Category
            import uuid
            import shutil
            
            print("=== Auto-fixing categories and images for Azure ===")
            
            # Ensure media directory exists
            os.makedirs('media', exist_ok=True)
            
            # Create default category image if it doesn't exist
            default_img_path = os.path.join('media', 'default-category.jpg')
            if not os.path.exists(default_img_path):
                # Create a simple blue square as placeholder
                try:
                    from PIL import Image
                    img = Image.new('RGB', (300, 300), color=(73, 109, 137))
                    img.save(default_img_path)
                    print(f"Created default category image at {default_img_path}")
                except Exception as e:
                    # If PIL fails, create an empty file
                    with open(default_img_path, 'wb') as f:
                        f.write(b"PLACEHOLDER")
                    print(f"Created placeholder file at {default_img_path}")
            
            # Ensure categories exist
            categories = [
                'Romance', 'Drama', 'Science', 'Computers', 'Philosophy', 
                'Mystery', 'Mythology', 'Manga', 'Thriller', 'Entrepreneur', 
                'Computer', 'History', 'Law', 'Fiction', 'Nature', 'Engineering'
            ]
            
            for title in categories:
                try:
                    if not Category.objects.filter(title=title).exists():
                        cid = f"cat_{uuid.uuid4().hex[:8]}"
                        Category.objects.create(
                            title=title,
                            cid=cid,
                            image='default-category.jpg'
                        )
                        print(f"Created missing category: {title}")
                    else:
                        # Ensure category has an image
                        cat = Category.objects.get(title=title)
                        if not cat.image or not os.path.exists(os.path.join('media', str(cat.image))):
                            cat.image = 'default-category.jpg'
                            cat.save()
                            print(f"Fixed image for category: {title}")
                except Exception as e:
                    print(f"Error fixing category {title}: {str(e)}")
            
            # Ensure test user exists for emergency access
            try:
                User = get_user_model()
                if not User.objects.filter(email='test@example.com').exists():
                    User.objects.create_user(
                        email='test@example.com',
                        username='emergency',
                        password='AdminAccess123!',
                        full_name='Emergency Access',
                        is_staff=True,
                        is_superuser=True
                    )
                    print("Created emergency admin user: test@example.com / AdminAccess123!")
            except Exception as e:
                print(f"Error creating emergency user: {str(e)}")
            
            print("=== Auto-fix complete ===")
