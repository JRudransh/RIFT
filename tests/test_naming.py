from rift.core.naming import object_names, pluralize, snake_case


def test_naming_normalization():
    assert snake_case("Hotel Room") == "hotel_room"
    assert pluralize("category") == "categories"
    names = object_names("Blog Post")
    assert names.pascal == "BlogPost"
    assert names.collection == "blog_posts"
    assert names.ops == "BlogPostOps"
