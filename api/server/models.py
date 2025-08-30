import hashlib
import random
import string
import uuid

from django.db import models
from django.utils import timezone


class Site(models.Model):
    """
    Represents a website being tracked in the analytics system.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the site",
    )
    user_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="User ID of the site owner (from Clerk)",
    )
    name = models.CharField(max_length=255, help_text="The name of the site")
    identifier = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique woodland-themed identifier (e.g., mossy-acorn-123456)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.identifier})"

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.generate_identifier()
        super().save(*args, **kwargs)

    def generate_identifier(self):
        """
        Generates a unique woodland-themed identifier for the site.
        Format: adjective-noun-XXXXXX (e.g., mossy-acorn-8K2PN9)
        """
        # Woodland-themed adjectives (200)
        adjectives = [
            # Original 30
            "mossy",
            "ancient",
            "twisted",
            "golden",
            "silver",
            "whispering",
            "hidden",
            "enchanted",
            "misty",
            "wild",
            "verdant",
            "shadowy",
            "dappled",
            "rustling",
            "peaceful",
            "mighty",
            "gentle",
            "dancing",
            "singing",
            "sleeping",
            "dreaming",
            "glowing",
            "sparkling",
            "silent",
            "eternal",
            "mystic",
            "sacred",
            "blessed",
            "haunted",
            "luminous",
            # Nature descriptors
            "dewy",
            "fragrant",
            "blooming",
            "budding",
            "sprouting",
            "growing",
            "flourishing",
            "thriving",
            "weathered",
            "gnarled",
            "knotted",
            "hollow",
            "fallen",
            "standing",
            "leaning",
            "bending",
            "swaying",
            "trembling",
            "shivering",
            "quivering",
            "still",
            "moving",
            "flowing",
            "trickling",
            "babbling",
            "gurgling",
            "splashing",
            "dripping",
            "soaking",
            "damp",
            # Colors and light
            "amber",
            "emerald",
            "jade",
            "copper",
            "bronze",
            "ivory",
            "ebony",
            "crimson",
            "scarlet",
            "violet",
            "indigo",
            "turquoise",
            "azure",
            "cerulean",
            "ochre",
            "umber",
            "sienna",
            "russet",
            "tawny",
            "dun",
            "grey",
            "ashen",
            "smoky",
            "dusky",
            "twilight",
            "dawn",
            "dusk",
            "moonlit",
            "starlit",
            "sunlit",
            # Textures and qualities
            "smooth",
            "rough",
            "soft",
            "hard",
            "fuzzy",
            "prickly",
            "thorny",
            "silky",
            "velvety",
            "feathery",
            "downy",
            "fluffy",
            "tangled",
            "woven",
            "matted",
            "braided",
            "coiled",
            "spiraling",
            "branching",
            "forked",
            "split",
            "cracked",
            "broken",
            "whole",
            "perfect",
            "flawed",
            "pure",
            "mixed",
            "blended",
            "layered",
            # Seasons and weather
            "spring",
            "summer",
            "autumn",
            "winter",
            "seasonal",
            "evergreen",
            "deciduous",
            "perennial",
            "annual",
            "frosty",
            "frozen",
            "thawing",
            "melting",
            "warming",
            "cooling",
            "windy",
            "breezy",
            "gusty",
            "calm",
            "stormy",
            "rainy",
            "sunny",
            "cloudy",
            "foggy",
            "hazy",
            "clear",
            "bright",
            "dim",
            "dark",
            "light",
            # Mystical and emotional
            "magical",
            "mystical",
            "ethereal",
            "otherworldly",
            "earthly",
            "grounded",
            "floating",
            "drifting",
            "wandering",
            "roaming",
            "exploring",
            "discovering",
            "knowing",
            "wise",
            "young",
            "old",
            "timeless",
            "ageless",
            "joyful",
            "merry",
            "cheerful",
            "somber",
            "solemn",
            "playful",
            "serious",
            "mysterious",
            "secretive",
            "revealing",
            "concealing",
            "protecting",
            # More nature qualities
            "natural",
            "untamed",
            "cultivated",
            "pruned",
            "overgrown",
            "undergrown",
            "towering",
            "miniature",
            "giant",
            "tiny",
            "massive",
            "delicate",
            "sturdy",
            "fragile",
            "resilient",
            "flexible",
            "rigid",
            "supple",
            "dried",
            "fresh",
            "aged",
            "new",
            "renewed",
            "reborn",
            "dying",
            "living",
            "breathing",
            "resting",
            "waking",
            "stirring",
        ]

        # Woodland-themed nouns (200)
        nouns = [
            # Original 30
            "oak",
            "pine",
            "birch",
            "willow",
            "maple",
            "cedar",
            "acorn",
            "mushroom",
            "fern",
            "moss",
            "brook",
            "stream",
            "clearing",
            "hollow",
            "grove",
            "canopy",
            "roots",
            "branch",
            "leaf",
            "squirrel",
            "deer",
            "owl",
            "fox",
            "badger",
            "rabbit",
            "hedgehog",
            "robin",
            "wren",
            "beetle",
            "firefly",
            # Trees
            "elm",
            "ash",
            "beech",
            "hickory",
            "walnut",
            "chestnut",
            "sycamore",
            "poplar",
            "aspen",
            "alder",
            "hawthorn",
            "rowan",
            "yew",
            "fir",
            "spruce",
            "hemlock",
            "larch",
            "cypress",
            "redwood",
            "sequoia",
            "juniper",
            "hazel",
            "holly",
            "laurel",
            "magnolia",
            "dogwood",
            "cherry",
            "apple",
            "pear",
            "plum",
            # Forest features
            "thicket",
            "copse",
            "wood",
            "forest",
            "jungle",
            "rainforest",
            "understory",
            "overstory",
            "floor",
            "trail",
            "path",
            "road",
            "bridge",
            "crossing",
            "ford",
            "bank",
            "shore",
            "edge",
            "border",
            "boundary",
            "heart",
            "center",
            "depths",
            "heights",
            "valley",
            "hill",
            "mountain",
            "cliff",
            "ravine",
            "gulch",
            # Water features
            "river",
            "creek",
            "spring",
            "waterfall",
            "cascade",
            "rapids",
            "pool",
            "pond",
            "lake",
            "marsh",
            "swamp",
            "bog",
            "wetland",
            "fen",
            "mire",
            "puddle",
            "drop",
            "mist",
            "fog",
            "dew",
            "rain",
            "snow",
            "ice",
            "frost",
            # Plants and fungi
            "vine",
            "ivy",
            "bramble",
            "thorn",
            "thistle",
            "nettle",
            "flower",
            "blossom",
            "bloom",
            "petal",
            "stem",
            "stalk",
            "grass",
            "reed",
            "rush",
            "sedge",
            "herb",
            "shrub",
            "bush",
            "hedge",
            "lichen",
            "fungus",
            "toadstool",
            "truffle",
            "spore",
            "mycelium",
            "bracket",
            "puffball",
            "morel",
            "chanterelle",
            # Animals
            "bear",
            "wolf",
            "lynx",
            "bobcat",
            "cougar",
            "moose",
            "elk",
            "caribou",
            "boar",
            "porcupine",
            "beaver",
            "otter",
            "mink",
            "weasel",
            "ferret",
            "stoat",
            "marten",
            "fisher",
            "raccoon",
            "opossum",
            "skunk",
            "chipmunk",
            "vole",
            "mouse",
            "shrew",
            "mole",
            "bat",
            "hawk",
            "eagle",
            "falcon",
            # Birds
            "raven",
            "crow",
            "jay",
            "cardinal",
            "finch",
            "sparrow",
            "warbler",
            "thrush",
            "blackbird",
            "starling",
            "swallow",
            "swift",
            "woodpecker",
            "nuthatch",
            "chickadee",
            "titmouse",
            "creeper",
            "kingfisher",
            "heron",
            "crane",
            "duck",
            "goose",
            "swan",
            "grouse",
            # Insects and small creatures
            "butterfly",
            "moth",
            "dragonfly",
            "damselfly",
            "bee",
            "wasp",
            "ant",
            "termite",
            "spider",
            "centipede",
            "millipede",
            "snail",
            "slug",
            "worm",
            "caterpillar",
            "chrysalis",
            "cocoon",
            "cricket",
            "grasshopper",
            "mantis",
            "cicada",
            "aphid",
            "ladybug",
            "weevil",
            # Natural objects
            "stone",
            "rock",
            "boulder",
            "pebble",
            "crystal",
            "mineral",
            "soil",
            "earth",
            "clay",
            "sand",
            "loam",
            "humus",
            "log",
            "stump",
            "snag",
            "burl",
            "knot",
            "bark",
            "sap",
            "resin",
            "amber",
            "needle",
            "cone",
            "nut",
            "seed",
            "berry",
            "fruit",
            "twig",
            "stick",
            "splinter",
        ]

        while True:
            # Pick random adjective and noun
            adjective = random.choice(adjectives)
            noun = random.choice(nouns)

            # Generate 6-character hash with letters and numbers (uppercase)
            hash_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

            # Combine into identifier
            identifier = f"{adjective}-{noun}-{hash_part}"

            # Check if this identifier already exists
            if not Site.objects.filter(identifier=identifier).exists():
                return identifier


class Session(models.Model):
    """
    Represents a user session for analytics tracking.
    Sessions are generated without cookies using IP + User Agent + Time Window.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the session",
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="The site this session belongs to",
    )

    session_id = models.CharField(
        max_length=64,
        db_index=True,
        unique=True,
        help_text="Anonymous session identifier (generated from IP + UA + time window)",
    )

    # Session metrics
    is_bounce = models.BooleanField(default=True, help_text="Whether this session only had one page view")
    duration = models.IntegerField(default=0, help_text="Duration of the session in seconds")
    page_view_count = models.IntegerField(default=0, help_text="Number of page views in this session")

    # Referrer for the session (first page view)
    referrer = models.URLField(max_length=2048, blank=True, help_text="Referrer URL for the session")
    referrer_domain = models.CharField(max_length=255, blank=True, help_text="Domain of the referrer")

    enter_page = models.CharField(max_length=1024, help_text="First page visited in this session")
    exit_page = models.CharField(max_length=1024, blank=True, help_text="Last page visited in this session")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.site.identifier} session: {self.session_id[:8]}..."

    @classmethod
    def generate_session_id(cls, ip_address, user_agent, timestamp=None):
        """
        Generate a privacy-focused session ID based on:
        - IP address (will be hashed)
        - User agent
        - Time window (30-minute buckets)

        This allows tracking sessions without cookies or persistent storage.
        Sessions expire after 30 minutes of inactivity.
        """
        if timestamp is None:
            timestamp = timezone.now()

        # Round timestamp to 30-minute windows
        minutes = timestamp.minute
        rounded_minutes = (minutes // 30) * 30
        time_bucket = timestamp.replace(minute=rounded_minutes, second=0, microsecond=0)

        # Create session identifier
        session_string = f"{ip_address}:{user_agent}:{time_bucket.isoformat()}"
        session_id = hashlib.sha256(session_string.encode()).hexdigest()

        return session_id

    def update_metrics(self):
        """
        Update session metrics based on page views.
        Called after a new page view is added to recalculate session statistics.
        """
        page_views = self.page_views.order_by("created_at")
        count = page_views.count()

        if count > 0:
            self.page_view_count = count
            self.is_bounce = count == 1

            if count > 1:
                first_view = page_views.first()
                last_view = page_views.last()
                self.duration = int((last_view.created_at - first_view.created_at).total_seconds())
                self.exit_page = last_view.path

            self.save()


class PageView(models.Model):
    """
    Represents a single page view event in the analytics system.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the page view",
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="page_views",
        help_text="The site this page view belongs to",
    )

    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="page_views",
        help_text="The session this page view belongs to (assigned async)",
    )

    # URL and page information
    url = models.URLField(max_length=2048, help_text="Full URL of the page viewed")
    path = models.CharField(max_length=1024, help_text="Path portion of the URL")

    # Referrer information
    referrer = models.URLField(max_length=2048, blank=True, help_text="Referrer URL if available")
    referrer_domain = models.CharField(max_length=255, blank=True, help_text="Domain of the referrer")

    # User identification (for session assignment)
    ip_hash = models.CharField(max_length=64, help_text="Hashed IP address for privacy")
    user_agent = models.TextField(help_text="Full user agent string")

    # Device information (parsed from user agent)
    browser = models.CharField(max_length=50, blank=True, help_text="Browser name")
    browser_version = models.CharField(max_length=20, blank=True, help_text="Browser version")
    operating_system = models.CharField(max_length=50, blank=True, help_text="Operating system")
    device_type = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
            ("bot", "Bot"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
        help_text="Type of device",
    )

    # Location information (parsed from IP)
    country = models.CharField(max_length=2, blank=True, help_text="ISO 3166-1 alpha-2 country code")
    region = models.CharField(max_length=255, blank=True, help_text="Region/state name")
    city = models.CharField(max_length=255, blank=True, help_text="City name")

    # Processing status
    is_processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether session assignment has been processed",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Index for finding unprocessed page views
            models.Index(fields=["is_processed", "created_at"]),
        ]

    def __str__(self):
        return f"{self.site.identifier}: {self.path} at {self.created_at}"

    def save(self, *args, **kwargs):
        from urllib.parse import urlparse

        # Extract path from URL if not provided
        if self.url and not self.path:
            parsed = urlparse(self.url)
            self.path = parsed.path or "/"

        # Extract referrer domain if referrer is provided
        if self.referrer and not self.referrer_domain:
            parsed = urlparse(self.referrer)
            self.referrer_domain = parsed.netloc

        super().save(*args, **kwargs)


class HourlyPageViewStats(models.Model):
    """
    Hourly aggregated statistics for page views by site.
    Updated via batch processing to provide fast analytics queries.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the hourly stats record",
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="hourly_stats",
        help_text="The site these stats belong to",
    )

    # Time bucket (UTC hour)
    hour_bucket = models.DateTimeField(
        db_index=True,
        help_text="UTC hour bucket (e.g., 2024-01-15 14:00:00+00:00 for 2-3 PM UTC)",
    )

    # Aggregated metrics
    pageview_count = models.IntegerField(
        default=0,
        help_text="Total page views in this hour",
    )
    unique_session_count = models.IntegerField(
        default=0,
        help_text="Number of unique sessions that had page views in this hour",
    )

    # Processing metadata
    last_processed_pageview_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the last pageview that was processed into this aggregation",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-hour_bucket"]
        unique_together = ["site", "hour_bucket"]
        indexes = [
            models.Index(fields=["site", "hour_bucket"]),
            models.Index(fields=["hour_bucket"]),
        ]
        db_table = "server_hourly_pageviews"

    def __str__(self):
        return f"{self.site.identifier}: {self.hour_bucket} ({self.pageview_count} views)"


class DailyPageViewStats(models.Model):
    """
    Daily aggregated statistics for page views by site.
    Updated via batch processing to provide fast analytics queries.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the daily stats record",
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="daily_stats",
        help_text="The site these stats belong to",
    )

    # Time bucket (UTC day)
    day_bucket = models.DateField(
        db_index=True,
        help_text="UTC day bucket (e.g., 2024-01-15 for January 15th, 2024)",
    )

    # Aggregated metrics
    pageview_count = models.IntegerField(
        default=0,
        help_text="Total page views in this day",
    )
    unique_session_count = models.IntegerField(
        default=0,
        help_text="Number of unique sessions that had page views in this day",
    )

    # Processing metadata
    last_processed_pageview_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the last pageview that was processed into this aggregation",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-day_bucket"]
        unique_together = ["site", "day_bucket"]
        indexes = [
            models.Index(fields=["site", "day_bucket"]),
            models.Index(fields=["day_bucket"]),
        ]
        db_table = "server_daily_pageviews"

    def __str__(self):
        return f"{self.site.identifier}: {self.day_bucket} ({self.pageview_count} views)"
