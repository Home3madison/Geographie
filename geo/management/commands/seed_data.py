from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from geo.models import Answer, Attraction, GeographicObject, Question, Quiz, Region


class Command(BaseCommand):
    help = 'Заполнение базы тестовыми данными по географии Кыргызстана'

    @staticmethod
    def _create_quiz_with_questions(title, description, questions_data):
        quiz, created = Quiz.objects.get_or_create(
            title=title,
            defaults={'description': description},
        )

        if not created and quiz.questions.exists():
            return

        if not quiz.description:
            quiz.description = description
            quiz.save(update_fields=['description'])

        for item in questions_data:
            question = Question.objects.create(quiz=quiz, text=item['text'])
            Answer.objects.bulk_create(
                [
                    Answer(question=question, text=option, is_correct=(idx == item['correct_index']))
                    for idx, option in enumerate(item['options'])
                ]
            )

    @staticmethod
    def _move_media_files():
        media_root = Path(settings.MEDIA_ROOT)
        target_dirs = {
            'regions': media_root / 'regions',
            'objects': media_root / 'objects',
            'attractions': media_root / 'attractions',
        }
        for directory in target_dirs.values():
            directory.mkdir(parents=True, exist_ok=True)

        file_map = {
            'regions': [
                'баткенская_область.jpg',
                'Джалал_абадская_область.png',
                'Иссык_кульская_область.jpg',
                'Нарынская_область.jpg',
                'Ошская_область.jpg',
                'Талаская_область.jpg',
                'Чуйская_область.jpg',
            ],
            'objects': [
                'Озеро_Иссык_Куль.jpg',
                'park-ala-archa.jpg',
                'Перевал_Торугарт.jpg',
                'Заповедник_Сары_Челек.jpg',
                'Гора_Сулайман_Тоо.jpg',
                'Ущелье_Каравшин.jpg',
                'Река_Талас.jpg',
            ],
            'attractions': [
                'Башня_Бурана.jpg',
                'Каракольское_ущелье.jpg',
                'Ореховые_леса_Арсланбоб.jpg',
                'Пик_Манас.jpg',
                'Священная_гора_Сулайман-Тоо.jpg',
                'Айгуль_Таш.jpg',
            ],
        }

        for folder, filenames in file_map.items():
            for filename in filenames:
                src = media_root / filename
                dst = target_dirs[folder] / filename
                if src.exists() and src != dst:
                    src.replace(dst)

    @staticmethod
    def _assign_images():
        region_images = {
            'Баткенская область': 'regions/баткенская_область.jpg',
            'Джалал-Абадская область': 'regions/Джалал_абадская_область.png',
            'Иссык-Кульская область': 'regions/Иссык_кульская_область.jpg',
            'Нарынская область': 'regions/Нарынская_область.jpg',
            'Ошская область': 'regions/Ошская_область.jpg',
            'Таласская область': 'regions/Талаская_область.jpg',
            'Чуйская область': 'regions/Чуйская_область.jpg',
        }

        object_images = {
            'Озеро Иссык-Куль': 'objects/Озеро_Иссык_Куль.jpg',
            'Ущелье Ала-Арча': 'objects/park-ala-archa.jpg',
            'Перевал Торугарт': 'objects/Перевал_Торугарт.jpg',
            'Заповедник Сары-Челек': 'objects/Заповедник_Сары_Челек.jpg',
            'Гора Сулайман-Тоо': 'objects/Гора_Сулайман_Тоо.jpg',
            'Ущелье Каравшин': 'objects/Ущелье_Каравшин.jpg',
            'Река Талас': 'objects/Река_Талас.jpg',
        }

        attraction_images = {
            'Башня Бурана': 'attractions/Башня_Бурана.jpg',
            'Каракольское ущелье': 'attractions/Каракольское_ущелье.jpg',
            'Ореховые леса Арсланбоб': 'attractions/Ореховые_леса_Арсланбоб.jpg',
            'Пик Манас': 'attractions/Пик_Манас.jpg',
            'Священная гора Сулайман-Тоо': 'attractions/Священная_гора_Сулайман-Тоо.jpg',
            'Айгуль-Таш': 'attractions/Айгуль_Таш.jpg',
        }

        use_cloudinary = bool(getattr(settings, 'USE_CLOUDINARY', False))
        media_root = Path(settings.BASE_DIR) / 'media'

        def assign(model, name, image_path):
            instance = model.objects.filter(name=name).first()
            if not instance:
                return

            if use_cloudinary:
                image_field = instance.image
                current_name = image_field.name if image_field else ''
                # Если в БД уже cloudinary-путь (не seed-путь) — не дублируем загрузку.
                if current_name and current_name != image_path:
                    return

                local_file = media_root / image_path
                if not local_file.exists():
                    return

                with local_file.open('rb') as fh:
                    image_field.save(local_file.name, File(fh), save=True)
            else:
                model.objects.filter(pk=instance.pk).update(image=image_path)

        for name, image_path in region_images.items():
            assign(Region, name, image_path)

        for name, image_path in object_images.items():
            assign(GeographicObject, name, image_path)

        for name, image_path in attraction_images.items():
            assign(Attraction, name, image_path)

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        self._move_media_files()

        regions_data = [
            {
                'name': 'Баткенская область',
                'description': 'Юго-западный регион с живописными горами, каньонами и богатой историей Великого Шёлкового пути.',
                'administrative_center': 'Баткен',
                'area': 17048,
                'population': 590000,
            },
            {
                'name': 'Джалал-Абадская область',
                'description': 'Один из крупнейших регионов страны, известный ореховыми лесами Арсланбоба и курортными зонами.',
                'administrative_center': 'Джалал-Абад',
                'area': 33700,
                'population': 1280000,
            },
            {
                'name': 'Иссык-Кульская область',
                'description': 'Известна озером Иссык-Куль, горными хребтами и туристическими маршрутами.',
                'administrative_center': 'Каракол',
                'area': 43700,
                'population': 520000,
            },
            {
                'name': 'Нарынская область',
                'description': 'Высокогорный регион с пастбищами, перевалами и красивыми ущельями.',
                'administrative_center': 'Нарын',
                'area': 45200,
                'population': 310000,
            },
            {
                'name': 'Ошская область',
                'description': 'Южный аграрный регион с древними городами, плодородными долинами и горными массивами Алая.',
                'administrative_center': 'Ош',
                'area': 29000,
                'population': 1500000,
            },
            {
                'name': 'Таласская область',
                'description': 'Небольшой, но исторически важный регион на северо-западе Кыргызстана, связанный с эпосом «Манас».',
                'administrative_center': 'Талас',
                'area': 11400,
                'population': 290000,
            },
            {
                'name': 'Чуйская область',
                'description': 'Регион на севере Кыргызстана с развитой инфраструктурой и плодородными долинами.',
                'administrative_center': 'Бишкек',
                'area': 20200,
                'population': 1000000,
            },
        ]

        regions = {}
        for data in regions_data:
            region, _ = Region.objects.update_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'administrative_center': data['administrative_center'],
                    'area': data['area'],
                    'population': data['population'],
                },
            )
            regions[data['name']] = region

        GeographicObject.objects.get_or_create(
            name='Озеро Иссык-Куль',
            defaults={
                'description': 'Крупнейшее высокогорное озеро Кыргызстана и важный туристический центр.',
                'object_type': GeographicObject.ObjectType.LAKE,
                'region': regions['Иссык-Кульская область'],
                'location': 'Иссык-Кульская котловина',
                'map_link': 'https://www.google.com/maps?q=Issyk+Kul&output=embed',
            },
        )
        GeographicObject.objects.get_or_create(
            name='Ущелье Ала-Арча',
            defaults={
                'description': 'Популярное горное ущелье и национальный парк рядом с Бишкеком.',
                'object_type': GeographicObject.ObjectType.GORGE,
                'region': regions['Чуйская область'],
                'location': 'Чуйская область, 40 км от Бишкека',
                'map_link': 'https://www.google.com/maps?q=Ala+Archa&output=embed',
            },
        )
        GeographicObject.objects.get_or_create(
            name='Перевал Торугарт',
            defaults={
                'description': 'Высокогорный перевал на границе Кыргызстана и Китая.',
                'object_type': GeographicObject.ObjectType.PASS,
                'region': regions['Нарынская область'],
                'location': 'Нарынская область',
                'map_link': 'https://www.google.com/maps?q=Torugart+Pass&output=embed',
            },
        )
        GeographicObject.objects.get_or_create(
            name='Заповедник Сары-Челек',
            defaults={
                'description': 'Биосферный заповедник с озёрной системой и уникальными орехово-плодовыми лесами.',
                'object_type': GeographicObject.ObjectType.RESERVE,
                'region': regions['Джалал-Абадская область'],
                'location': 'Аксыйский район',
                'map_link': 'https://www.google.com/maps?q=Sary+Chelek&output=embed',
            },
        )
        GeographicObject.objects.get_or_create(
            name='Гора Сулайман-Тоо',
            defaults={
                'description': 'Священная гора в городе Ош, включённая в список всемирного наследия ЮНЕСКО.',
                'object_type': GeographicObject.ObjectType.MOUNTAIN,
                'region': regions['Ошская область'],
                'location': 'г. Ош',
                'map_link': 'https://www.google.com/maps?q=Sulaiman+Too&output=embed',
            },
        )
        GeographicObject.objects.get_or_create(
            name='Ущелье Каравшин',
            defaults={
                'description': 'Известный район альпинизма и треккинга в Памиро-Алае.',
                'object_type': GeographicObject.ObjectType.GORGE,
                'region': regions['Баткенская область'],
                'location': 'Ляйлякский район',
                'map_link': 'https://www.google.com/maps?q=Karavshin+Valley&output=embed',
            },
        )
        GeographicObject.objects.get_or_create(
            name='Река Талас',
            defaults={
                'description': 'Основная водная артерия Таласской долины.',
                'object_type': GeographicObject.ObjectType.RIVER,
                'region': regions['Таласская область'],
                'location': 'Таласская область',
                'map_link': 'https://www.google.com/maps?q=Talas+River&output=embed',
            },
        )

        Attraction.objects.get_or_create(
            name='Башня Бурана',
            defaults={
                'description': 'Историко-археологический комплекс в Чуйской области.',
                'region': regions['Чуйская область'],
            },
        )
        Attraction.objects.get_or_create(
            name='Каракольское ущелье',
            defaults={
                'description': 'Живописное место для треккинга и экотуризма.',
                'region': regions['Иссык-Кульская область'],
            },
        )
        Attraction.objects.get_or_create(
            name='Ореховые леса Арсланбоб',
            defaults={
                'description': 'Один из крупнейших ореховых массивов в мире и популярный эко-маршрут.',
                'region': regions['Джалал-Абадская область'],
            },
        )
        Attraction.objects.get_or_create(
            name='Пик Манас',
            defaults={
                'description': 'Известная вершина Таласского хребта, важная для горного туризма региона.',
                'region': regions['Таласская область'],
            },
        )
        Attraction.objects.get_or_create(
            name='Священная гора Сулайман-Тоо',
            defaults={
                'description': 'Культурно-исторический символ юга Кыргызстана.',
                'region': regions['Ошская область'],
            },
        )
        Attraction.objects.get_or_create(
            name='Айгуль-Таш',
            defaults={
                'description': 'Природный памятник Баткенской области, известный редким цветком айгуль.',
                'region': regions['Баткенская область'],
            },
        )

        quizzes_data = [
            {
                'title': 'Базовый тест по географии Кыргызстана',
                'description': 'Проверка основных знаний о регионах и природных объектах.',
                'questions': [
                    {
                        'text': 'Какое озеро является крупнейшим в Кыргызстане?',
                        'options': ['Сон-Куль', 'Иссык-Куль', 'Сары-Челек'],
                        'correct_index': 1,
                    },
                    {
                        'text': 'Административный центр Иссык-Кульской области:',
                        'options': ['Нарын', 'Каракол', 'Ош'],
                        'correct_index': 1,
                    },
                    {
                        'text': 'Какой регион является высокогорным и известен перевалами?',
                        'options': ['Нарынская область', 'Таласская область', 'Баткенская область'],
                        'correct_index': 0,
                    },
                ],
            },
            {
                'title': 'Озёра и реки Кыргызстана',
                'description': 'Тест по водным ресурсам страны.',
                'questions': [
                    {
                        'text': 'Какая река считается одной из главных в Кыргызстане?',
                        'options': ['Нарын', 'Амударья', 'Иртыш'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Какое озеро находится в Иссык-Кульской области?',
                        'options': ['Иссык-Куль', 'Балхаш', 'Алаколь'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Сары-Челек относится к типу:',
                        'options': ['Высокогорных озёр', 'Искусственных водохранилищ', 'Морей'],
                        'correct_index': 0,
                    },
                ],
            },
            {
                'title': 'Горы и перевалы',
                'description': 'Проверка знаний о горных районах и перевалах Кыргызстана.',
                'questions': [
                    {
                        'text': 'Перевал Торугарт находится в:',
                        'options': ['Нарынской области', 'Чуйской области', 'Таласской области'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Сулайман-Тоо расположен в городе:',
                        'options': ['Ош', 'Бишкек', 'Каракол'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Ущелье Каравшин известно как район:',
                        'options': ['Альпинизма и треккинга', 'Морского отдыха', 'Пустынного туризма'],
                        'correct_index': 0,
                    },
                ],
            },
            {
                'title': 'Области Кыргызстана',
                'description': 'Тест по административному делению и центрам областей.',
                'questions': [
                    {
                        'text': 'Административный центр Джалал-Абадской области:',
                        'options': ['Джалал-Абад', 'Талас', 'Баткен'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Какая область имеет центр в Караколе?',
                        'options': ['Иссык-Кульская', 'Ошская', 'Чуйская'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Талас является центром какой области?',
                        'options': ['Таласской', 'Нарынской', 'Баткенской'],
                        'correct_index': 0,
                    },
                ],
            },
            {
                'title': 'Заповедники и природные территории',
                'description': 'Тест о природоохранных территориях Кыргызстана.',
                'questions': [
                    {
                        'text': 'Сары-Челек — это:',
                        'options': ['Биосферный заповедник', 'Столица области', 'Горный перевал'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Ала-Арча известна как:',
                        'options': ['Национальный парк', 'Песчаная пустыня', 'Морской порт'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Айгуль-Таш находится в:',
                        'options': ['Баткенской области', 'Чуйской области', 'Нарынской области'],
                        'correct_index': 0,
                    },
                ],
            },
            {
                'title': 'Культурные и исторические места',
                'description': 'Проверка знаний о культурном наследии Кыргызстана.',
                'questions': [
                    {
                        'text': 'Башня Бурана расположена в:',
                        'options': ['Чуйской области', 'Ошской области', 'Иссык-Кульской области'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Сулайман-Тоо включена в список:',
                        'options': ['ЮНЕСКО', 'ОПЕК', 'ШОС'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Ореховые леса Арсланбоб находятся в:',
                        'options': ['Джалал-Абадской области', 'Таласской области', 'Чуйской области'],
                        'correct_index': 0,
                    },
                ],
            },
            {
                'title': 'Туризм Кыргызстана',
                'description': 'Тест по популярным туристическим локациям страны.',
                'questions': [
                    {
                        'text': 'Каракольское ущелье популярно для:',
                        'options': ['Треккинга и экотуризма', 'Морских круизов', 'Сафари'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Пик Манас находится в:',
                        'options': ['Таласской области', 'Баткенской области', 'Иссык-Кульской области'],
                        'correct_index': 0,
                    },
                    {
                        'text': 'Иссык-Куль известен прежде всего как:',
                        'options': ['Курортный регион у высокогорного озера', 'Пустынный район', 'Лесная низменность'],
                        'correct_index': 0,
                    },
                ],
            },
        ]

        for quiz_data in quizzes_data:
            self._create_quiz_with_questions(
                title=quiz_data['title'],
                description=quiz_data['description'],
                questions_data=quiz_data['questions'],
            )

        self._assign_images()

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы.'))
