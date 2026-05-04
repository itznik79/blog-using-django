# Generated data migration to backfill Category rows from existing Post.category values
from django.db import migrations


def forwards(apps, schema_editor):
    Category = apps.get_model("blogs", "Category")
    Post = apps.get_model("blogs", "Post")
    from django.utils.text import slugify
    # Iterate posts and convert legacy string categories into Category rows
    for post in Post.objects.all():
        try:
            cat_val = getattr(post, "category", None)
        except Exception:
            # defensive: if attribute access fails, skip
            continue

        # If category is a string (legacy), create/find Category and assign
        if isinstance(cat_val, str):
            name_str = cat_val.strip()
            if not name_str:
                continue
            slug = slugify(name_str)[:160]
            cat, _ = Category.objects.get_or_create(name=name_str, defaults={"slug": slug})
            post.category = cat
            post.save()
        # If category is an int (unlikely here) or already a FK, skip


def reverse(apps, schema_editor):
    # No-op reverse: leaving created categories is fine
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("blogs", "0003_category_alter_post_category"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse, atomic=False),
    ]
