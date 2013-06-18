from django.core.urlresolvers import reverse

def steps_nav(user, selected):
    
    all_steps = [
            #'text'         
            #   'styling_class(es)',    
            #       'links_to'
            #           'permission_required'
            #               'selected'
            ['1. Review Message', 
                '',  
                    reverse('mypublisher:review'),
                        'staff',
                            'review',

            ],
            ['2. Publish Message', 
                '',  
                    reverse('mypublisher:checkout'),
                        'staff',
                            'publish',

            ]
        ]

    steps_nav = []
    for nn in all_steps:
        # style the selected option
        if nn[4] == selected:
            nn[1] = 'current'
        # permission?
        if nn[3] == 'any':
            steps_nav.append(nn)
        elif nn[3] == 'staff' and user.is_staff:
            steps_nav.append(nn)

    return steps_nav

