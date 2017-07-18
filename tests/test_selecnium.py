from selenium import webdriver

class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        '''Invoked before the tests in this class'''
        # Start Firefox
        try:
            cls.client = webdriver.Firefox()
        except:
            pass

        # Skip these tests if the brower could not be started
        if cls.client:
            # Create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # Suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            # Create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            # Add an administrator user
            admin_role = Role.query.filter_by(permission=0xff).first()
            admin = User(email='john@example.com',
                         username='john', password='cat',
                         role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # Start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()

        @classmethod
        def tearDownClass(cls):
            '''Invoked after the tests in this class'''
            if cls.client:
                # Stop the flask server and the browser
                cls.client.get('http://localhost:5000/shutdown')
                cls.client.close()

                # Destroy database
                db.drop_all()
                db.session.remove()

                # Remove application context
                cls.app_context.pop()
        
        def setUp(self):
            if not self.client:
                self.skipTest('Web browser not available')

        def tearDown(self):
            pass

        def test_admin_home_page(self):
            '''Test with Selenium
            When testing with Selenium, tests send commands to the web browser and never
            interact with the application directly. The commands closely match the actions
            that a real user would perform with mouse and keyboard.
            '''
            # Navigate to home page
            self.client.get('http://localhost:5000/')
            self.assertTrue(re.search('Hello,\s+Stranger!',
                                      self.client.page_source))
            
            # Navigation to login page
            self.client.find_element_by_link_text('Log In').click()
            self.assertTrue('<h1>Login</h1>' in self.client.page_source)

            # login
            self.client.find_element_by_name('email').send_keys(
                'john@example.com')
            self.client.find_element_by_name('password').send_keys('cat')
            self.client.find_element_by_name('submit').click()
            self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

            # Navigate to the user's profile page
            self.client.find_element_by_link_text('Profile').click()
            self.assertTrue('<h1>john</h1>' in self.client.page_source)