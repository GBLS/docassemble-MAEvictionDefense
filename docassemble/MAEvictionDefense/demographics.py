def gender_list() :
    return [
        ['female','Female'],
        ['male','Male'],
        ['non binary','Non-binary/third-gender'],
        ['self described','Prefer to self-describe'],
        ['unspecified','Prefer not to say']
    ]

def age_list(): 
    return [
      ['< 18','Under 18'],
      ['18-24','18-24 years old'],
      ['25-34','25-34 years old'],
      ['35-44','35-44 years old'],
      ['45-54','45-54 years old'],
      ['55-64','55-64 years old'],
      ['65-74','65-74 years old'],
      ['>= 75','75 years or older']
    ]

def ethnicity_list():
    return [
        ['white','White'],
        ['hispanic','Hispanic or Latino'],
        ['black','Black or African American'],
        ['native','Native American or American Indian'],
        ['asian','Asian / Pacific Islander'],
        ['other','Other']
    ]    

def education_list():
    return [
        ['none','No schooling completed'],
        ['<= 8th grade','Nursery school to 8th grade'],
        ['some high school','Some high school, no diploma'],
        ['high school','High school graduate, diploma or the equivalent (for example: GED)'],
        ['some college','Some college credit, no degree'],
        ['trade school','Trade/technical/vocational training'],
        ['associate','Associate degree'],
        ['bachelor','Bachelor’s degree'],
        ['masters',"Master’s degree"],
        ['professional','Professional degree'],
        ['doctorate','Doctorate degree']
    ]

def relationship_list():
    return {
        'child': 'Child',
        'cousin': 'Cousin',
        'foster child': 'Foster Child',
        'grandchild': 'Grand Child',
        'grandparent': 'Grandparent',
        'guardian': 'Guardian',
        'parent': 'Parent',
        'sibling': 'Sibling',
        'spouse': 'Spouse',
        'domestic partner': 'Domestic Partner',
        'step child': 'Step Child',
        'step parent': 'Step Parent',
        'unmarried partner': 'Unmarried Partner',
        'other': 'Other'
    }    