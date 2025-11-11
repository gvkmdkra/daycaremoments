"""
Fix Photo URLs in Existing Database
Updates all photo URLs to use working placehold.co service
"""

from app.database import get_db
from app.database.models import Photo

print("Fixing photo URLs in database...")

with get_db() as db:
    photos = db.query(Photo).all()

    fixed_count = 0
    for photo in photos:
        old_url = photo.url

        # Replace via.placeholder.com with placehold.co
        if "via.placeholder.com" in old_url:
            new_url = old_url.replace("via.placeholder.com", "placehold.co")
            new_url = new_url.replace("?text=", "/png?text=")

            photo.url = new_url
            photo.thumbnail_url = new_url
            fixed_count += 1

            print(f"Fixed: {photo.caption}")
            print(f"  Old: {old_url[:80]}")
            print(f"  New: {new_url[:80]}")

    db.commit()
    print(f"\nTotal photos fixed: {fixed_count}")
    print("Database updated successfully!")
