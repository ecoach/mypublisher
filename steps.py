from django.core.urlresolvers import reverse

def steps_nav(user, selected):
    
    all_steps = [
            #'text'         
            #   'styling_class(es)',    
            #       'links_to'
            #           'permission_required'
            #               'selected'
            ['Run Checkout', 
                '',  
                    reverse('mypublisher:run_checkout'),
                        'staff',
                            'run_checkout',

            ],
            ['Copy Student', 
                '',  
                    reverse('mypublisher:copycat'),
                        'staff',
                            'copycat',

            ],
            ['Review Messages', 
                '',  
                    reverse('mypublisher:message_review', kwargs={'msg_id':'home'}),
                        'staff',
                            'message_review',

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

