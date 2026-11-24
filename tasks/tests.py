from django.test import TestCase, Client
from django.contrib.auth.models import User
from tasks.models import Task

class TaskAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django App')

    def test_signup_page(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)

    def test_signin_flow(self):
        response = self.client.post('/signin/', {
            'username': self.username,
            'password': self.password
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_task_lifecycle(self):
        # Iniciar sesión
        self.client.login(username=self.username, password=self.password)

        # Crear tarea
        response = self.client.post('/tasks/create/', {
            'title': 'Comprar leche',
            'description': 'Ir al supermercado a comprar leche deslactosada',
            'important': True
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, 'Comprar leche')
        self.assertTrue(task.important)
        self.assertIsNone(task.datecompleted)

        # Listar pendientes
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comprar leche')

        # Completar tarea
        response = self.client.post(f'/tasks/{task.id}/complete/', follow=True)
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertIsNotNone(task.datecompleted)

        # Listar completadas
        response = self.client.get('/tasks_completed/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comprar leche')

        # Eliminar tarea
        response = self.client.post(f'/tasks/{task.id}/delete/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 0)

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/logout/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
