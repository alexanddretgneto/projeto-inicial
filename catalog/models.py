from django.db import models

# Importar reverse para gerar URLs com base nos padrões de URL definidos
from django.urls import reverse

class Genre(models.Model):
    """Modelo representando um gênero de livro (por exemplo, Ficção Científica, Não Ficção)."""
    name = models.CharField(
        max_length=200,
        help_text="Digite um gênero de livro (por exemplo, Ficção Científica, Poesia Francesa, etc.)"
    )

    def __str__(self):
        """String para representar o objeto do modelo (no site de Administração, etc.)"""
        return self.name


class Language(models.Model):
    """Modelo representando um Idioma (por exemplo, Inglês, Francês, Japonês, etc.)"""
    name = models.CharField(
        max_length=200,
        help_text="Digite o idioma do livro (por exemplo, Inglês, Francês, Japonês, etc.)"
    )

    def __str__(self):
        """String para representar o objeto do modelo (no site de Administração, etc.)"""
        return self.name


class Book(models.Model):
    """Modelo representando um livro (mas não uma cópia específica de um livro)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Chave Estrangeira usada porque um livro pode ter apenas um autor, mas os autores podem ter vários livros.
    # Autor é uma string em vez de um objeto porque ainda não foi declarado no arquivo.
    summary = models.TextField(max_length=1000, help_text="Digite uma breve descrição do livro")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='Número ISBN de 13 caracteres <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Selecione um gênero para este livro")
    # ManyToManyField usada porque um gênero pode conter muitos livros e um livro pode abranger muitos gêneros.
    # A classe Genre já foi definida, então podemos especificar o objeto acima.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title', 'author']

    def display_genre(self):
        """Cria uma string para o Gênero. Isso é necessário para exibir o gênero no Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Gênero'

    def get_absolute_url(self):
        """Retorna a URL para acessar uma instância específica do livro."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String para representar o objeto do modelo."""
        return self.title


import uuid  # Necessário para instâncias únicas de livros
from datetime import date

from django.contrib.auth.models import User  # Necessário para atribuir um usuário como um tomador de empréstimo

class BookInstance(models.Model):
    """Modelo representando uma cópia específica de um livro (ou seja, que pode ser emprestada da biblioteca)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="ID único para este livro específico em toda a biblioteca")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        """Determina se o livro está atrasado com base na data de vencimento e na data atual."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('d', 'Manutenção'),
        ('o', 'Emprestado'),
        ('a', 'Disponível'),
        ('r', 'Reservado'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Disponibilidade do livro'
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Definir livro como devolvido"),)

    def __str__(self):
        """String para representar o objeto do modelo."""
        return '{0} ({1})'.format(self.id, self.book.title)


class Author(models.Model):
    """Modelo representando um autor."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('falecido', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Retorna a URL para acessar uma instância específica do autor."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String para representar o objeto do modelo."""
        return '{0}, {1}'.format(self.last_name, self.first_name)