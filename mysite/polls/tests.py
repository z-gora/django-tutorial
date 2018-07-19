import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() + datetime.timedelta(minutes=-10)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() + datetime.timedelta(days=-30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTest(TestCase):
    def test_no_questions(self):
        # No questions in the database
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        # Questions with pub_date in the past should be displayed
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Past question")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question>']
        )

    def test_future_question(self):
        # Questions with pub_date in the future should not be displayed
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_question(self):
        # ONLY past questions are displayed
        create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Past question")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question>']
        )

    def test_future_and_past_question(self):
        # ONLY past questions are displayed
        create_question(question_text="Past question 1", days=-20)
        create_question(question_text="Past question 2", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Past question 1")
        self.assertContains(response, "Past question 2")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 1>', '<Question: Past question 2>']
        )


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Past question", days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code,404)

    def test_past_question(self):
        future_question = create_question(question_text="Future question", days=-30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)


class QuestionResultsViewTest(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Past question", days=30)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code,404)

    def test_past_question(self):
        future_question = create_question(question_text="Future question", days=-30)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)
