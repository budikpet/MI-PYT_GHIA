from flexmock import flexmock
from ghia.github.my_data_classes import Issue

fallback_label = "FallbackLabelName"
random_person = "random_person"

# Has fallback label, 1 random person
has_fallback_label = flexmock(title="DummyTitle",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=[],
    labels=[fallback_label],
    ppl_after_append=0,
    ppl_after_set=0,
    ppl_after_change=0,
    users_to_add=[]
    )

# No fallback label, 1 extra label and 1 random person
no_fallback_label = flexmock(title="DummyTitle",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=[random_person],
    labels=["random_label"],
    ppl_after_append=1,
    ppl_after_set=1,
    ppl_after_change=0,
    users_to_add=[]
    )

# Title location, 0 random person, add 1 person
in_title = flexmock(title="title_1",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=[],
    labels=["random_label"],
    ppl_after_append=1,
    ppl_after_set=1,
    ppl_after_change=1,
    users_to_add=["person_1"]
    )

# Text location, 1 random and 1 rule person, adds nobody
in_text = flexmock(title="DummyTitle",
    body="text_1",
    html_url="DummyUrl",
    number=1,
    assignees=[random_person, "person_1"],
    labels=["random_label"],
    ppl_after_append=2,
    ppl_after_set=2,
    ppl_after_change=1,
    users_to_add=["person_1"]
    )

# Label + text location, 1 random person, adds 2 people
in_label_text = flexmock(title="DummyTitle",
    body="text_2",
    html_url="DummyUrl",
    number=1,
    assignees=[random_person],
    labels=["label_1", "random_label"],
    ppl_after_append=3,
    ppl_after_set=1,
    ppl_after_change=2,
    users_to_add=["person_1", "person_2"]
    )

# Any location, 1 random person, adds 1 person
in_any = flexmock(title="any_2",
    body="DummyBody",
    html_url="DummyUrl",
    number=1,
    assignees=[random_person],
    labels=["random_label"],
    ppl_after_append=2,
    ppl_after_set=1,
    ppl_after_change=1,
    users_to_add=["person_2"]
    )