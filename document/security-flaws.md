# Cyber Security Project I (OWASP list 2017)

## Installation
The project application utilises Python’s Django framework. Because this project is part of the course Cyber Security, it is assumed that user has Python and Django installed. In addition, user must install Django Axes to ensure the correct functionality of the project application. Django Axes can be installed with command 
```
pip install django-axes[ipware]
```
 (see more about Django Axes: https://github.com/jazzband/django-axes). 

## Security flaws and fixes

### Flaw 1: A1 Injection
The project application’s function for sending messages is vulnerable to SQL-injection. The vulnerable version of the function utilises raw SQL and unsanitised data. The user provided data, namely the sent message, is directly concatenated to the query without parametrisation. The attacker can e.g. give admin privileges to themselves or drop data tables, which leads the application to fail. Utilising Django’s default object-relational mapping layer (ORM) is more secure choice than raw SQL. Django ORM is based on querysets that are protected against SQL-injection by query parameterisation.
In some cases, raw SQL provides more powerful queries than Django ORM. If utilising raw SQL is justifiable, it is important to sanitise the user provided data and parametrise the queries. Also, it might be relevant to prevent prevent multiple query execution at once (the vulnerable version of send message function utilises executionscript() instead of execute()). 

### Flaw 2: A2 Broken Authentication
#### Credential Stuffing
https://github.com/jazzband/django-axes
-	No limits on how many times user can attempt to login. Attacker may use the application for e.g. testing username-password -pairs or dictionary attack
-	How to fix:    
    -	Django axes  
        - if user has 3 unsuccessful login attempts, the account is locked for defined period of time (3 minutes at the moment for test reasons)
        -	compares username + IP-address combination to prevent denial of service attacks (if done only based on username, increases possibility of DoS attack) 
        -	logs all login failures to database automatically
#### Password Validation
https://docs.djangoproject.com/en/4.2/topics/auth/passwords/#module-django.contrib.auth.password_validation 
-	No rules for credentials e.g. password can be anything
-	How to fix:
    -	Django offers pluggable configurable password validators
    -	defaults:
        -	UserAttributeSimilarityValidator
            o	checks the similarity between the password and a set of attributes of the user (default ‘username’, ‘first_name’, ‘last_name’, ‘email’)
            o	max similarity 0.7, scale from 0.1 to 1.0
        -	MinimumLenghtValidator
            o	default 8
        -	CommonPasswordValidator
            o	compares password to list of 20,000 common passwords
            o	default list https://gist.github.com/roycewilliams/226886fd01572964e1431ac8afc999ce 
        -	NumericPasswordValidator
            o	checks whether the password isn’t entirely numeric
  -	Support for custom validators
#### Idle user log out
https://docs.djangoproject.com/en/4.2/topics/http/sessions/ 
-	After using the application, instead of logging oneself out, user simply closes the browser. If application session timeouts aren’t set correctly, user remains authenticated.
-	How to fix:
      -	automated log out after predefined idle time using session cookies (3 minutes at the moment for test reasons)
          -	checks the timestamp of the last sent http-request with session cookie, if exceeds the cookie age, shows error page and user must log in again
### Flaw 3: A5 Broken Access Control
-	Force browsing to authenticated pages as an unauthenticated user or to privileged pages as a standard user
-	Bypassing access control checks by modifying the URL
-	How to fix:
### Flaw 4:  A7 Cross-site script (not backend!)
-	
### Flaw 5: Cross-Site Request Forgery (CSRF) (not on the OWASP list)
-	User can be tricked to visit malicious webpage which contains broken image. When browser loads the page, spam-message is sent to every user of the application
-	How to fix:
    -	csrf-token
    - use method ‘POST’ instead of ‘GET’ 
