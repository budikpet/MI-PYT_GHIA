from flexmock import flexmock
from ghia.github.my_data_classes import Issue

fallback_label = "FallbackLabelName"

# Has fallback label, 1 random person
has_fallback_label = flexmock(title="DummyTitle",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=["random_person"],
    labels=[fallback_label])

# No fallback label, 1 extra label and 1 random person
no_fallback_label = flexmock(title="DummyTitle",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=["random_person"],
    labels=["random_label"])

# Title location, 1 random person, add 1 person
in_title = flexmock(title="title_1",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=["random_person"],
    labels=["random_label"])

# Text location, 1 random and 1 rule person, adds nobody
in_text = flexmock(title="DummyTitle",
    body="text_1",
    html_url="DummyUrl",
    number=1,
    assignees=["random_person", "person1"],
    labels=["random_label"])

# Label + text location, 1 random person, adds 2 people
in_label_text = flexmock(title="DummyTitle",
    body="text_2",
    html_url="DummyUrl",
    number=1,
    assignees=["random_person"],
    labels=["label_1", "random_label"])

# Any location, 1 random person, adds 1 person
in_any = flexmock(title="any_2",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=["random_person"],
    labels=["random_label"])