def 
    return '(profile {username: ' + id2username(profile) + ' } ) - [interaction : follows { weight: [ ' + getWeight() + ' ] } ] -> (neighbor {username: ' + id2username(neighbor) + ' } )' 
