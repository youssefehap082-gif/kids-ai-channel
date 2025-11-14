def generate_seo_variants(title, animal):
    variants = [title, f"Top facts about the {animal}", f"Amazing {animal} facts"]
    tags = [animal, 'wildlife', 'animals', f"{animal} facts", 'animal facts']
    description = title + '\n\n' + 'Discover amazing facts about the ' + animal + '.\n' + '#wildlife #animals'
    return {'titles':variants, 'tags':tags, 'description':description}
