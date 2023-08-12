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

In some cases, raw SQL provides more powerful queries than Django ORM. If utilising raw SQL is justifiable, it is important to sanitise the user provided data and parametrise the queries. Also, it might be relevant to prevent multiple query execution at once (the vulnerable version of send message function utilises executionscript() instead of execute()). 

### Flaw 2: A2 Broken Authentication
Broken authentication often arises due to improperly implemented authentication and session management functions. Authentication refers to the process of verifying the identity of users, typically through usernames and passwords, while session management involves maintaining and controlling the user's session after authentication.  

Credential stuffing, brute force or other automated attacks pose security threats for applications lacking limits for failed login attempts. In these attack methods, the attackers use lists of compromised user credentials to breach into a system. These methods are based on the assumption, that many users reuse usernames and passwords across multiple services.  

Allowing the use of default, weak, or well-known passwords grants attackers an easy access to user accounts.  While it is widely acknowledged that relying on weak passwords and using the same password for multiple accounts is inadvisable, these practices continue to be a common security oversight. Implementing restrictions against the use of default, weak, or well-known passwords within the application reduces the risk of unauthorised access to accounts.  

Session management constitutes the fundamental cornerstone of robust authentication and access controls. A session is created when user logs in successfully and session specific ID is given to the user. Proper session management requires e.g. that session ID is invalidated after logout, idle, and absolute timeouts to prevent any unauthorised access. Inadequately configured session timeouts, combined with users failing to log out, can lead to prolonged authentication. Especially when using public computers, this exposes potential security vulnerabilities.  

In the project application, credential stuffing attacks are prevented with help of Django Axes, a plugin for keeping track of suspicious login attempts. With Axes, the number of unsuccessful login attempts is limited to 3, after which the associated account is locked for 3 minutes (these are for test reasons, both are configurable). Axes compares username + IP-address combination to prevent denial of service (DoS) attacks. Comparing only username increases possibility of DoS attack when attackers can try to get access on multiple accounts from same IP-address and get them locked. After every successful login attempt, the login attempt calculator is reset to zero. Axes also logs all login failures to the database automatically.  
(Source: https://github.com/jazzband/django-axes)  

Weak password check is implemented in the project application with Django’s pluggable configurable password validators. The project application utilises a default set of validators: UserAttributeSimilarityValidator, MinimumLenghtValidator, CommonPasswordValidator and NumericPasswordValidator (the functionality of each validators are shortly explained  within the code). While these default validators constitute the foundational defence against weak passwords, they do not ensure the creation of truly strong passwords.  
(Source: https://docs.djangoproject.com/en/4.2/topics/auth/passwords/#module-django.contrib.auth.password_validation)  

The project application logs the user automatically out after 3 minutes idle time (this is for test reasons, configurable). Idle time check is done by comparing the timestamp of the last sent HTTP-request with session cookie age. If the timestamp exceeds the cookie age, user is logged out and redirected to the error page. This prevents unauthorised access to user account in cases where users forget to manually log out.  
(Source: https://docs.djangoproject.com/en/4.2/topics/http/sessions/)

### Flaw 3: A5 Broken Access Control
Access control ensures that users are confined within their designated permissions, preventing unauthorized actions. Broken access control allows attackers to bypass or circumvent the normal security controls checks. Poorly implemented access control permits force browsing to authenticated pages as an unauthenticated user or to privileged pages as a standard user. Furthermore, by manipulating the URL directly, attackers may bypass application’s access controls.  

Django provides several different kinds of access control mechanisms in form of decorators. Within the project application, pages restricted to logged in users, utilises login required -decorator to prevent unauthorised access. Privileged pages, namely the admin pages, are protected with custom admin check -decorator, which checks whether the user has the admin status or not. In case of not having the admin status, the user is redirected to login page. Without these decorators, attackers can bypass application login completely and a normal logged in user can get access to admin pages solely by modifying the URL in correct way.  
(Source: https://docs.djangoproject.com/en/4.2/topics/auth/default/#the-login-required-decorator, https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)  

In the project application, broken access control allows user to browse back to previous page, which requires login, even after successful logged out. This vulnerability is patched by controlling the caching of the pages. This solution might not be the best practice and the URLs of previous pages are still visible to the user even though the view of the corresponding page is not.

### Flaw 4:  A7 Cross-site script
Cross-Site Scripting (XSS) attacks are a type of injection, in which malicious scripts are injected into otherwise benign and trusted websites. XSS attacks occur when an attacker uses a web application to send malicious code, generally in the form of a browser side script, to a different end user. There are three main types of XSS attacks: reflected XSS, where the malicious script comes from the current HTTP request, stored XSS, where the malicious script comes from the website's database, and DOM-based XSS, where the vulnerability exists in client-side code rather than server-side code.  

The project application has vulnerability for XSS attack in the function for sending a message. The user provided data is not sanitised properly before inserting the data to the database. Furthermore, front end uses the Django safe filter, which renders HTML as-is without being escaped. This allows the attacker to send message to every user containing malicious scripts.  

Escaping HTML characters is a default setting in Django. However, if this feature is turned off, e.g. with safe filter, the data sanitation can be accomplished other ways. In the project application, the data is sanitised utilising Python built-in html module which converts characters &, < and > to HTML-safe sequences. This data sanitation approach renders the messages exactly as users entered them thus preventing the injection of any malicious scripts.  
(Source: https://docs.python.org/3/library/html.html)

### Flaw 5: Cross-Site Request Forgery (CSRF) (not on the OWASP 2017 list)
-	User can be tricked to visit malicious webpage which contains broken image. When browser loads the page, spam-message is sent to every user of the application
-	How to fix:
    -	csrf-token
    - use method ‘POST’ instead of ‘GET’ 
