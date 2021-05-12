# RestDoctor

BestDoctor's batteries for REST services.

## Для чего нужен RestDoctor

У нас в BestDoctor есть [свой API Guide](https://github.com/best-doctor/guides/blob/master/guides/api_guide.md), в котором написано, как API должно быть
построено. А еще у нас есть Django и довольно логично использовать Django Rest Framework. Он достаточно гибкий,
однако в некоторых местах мы хотим получить больше контроля и соблюдения своих правил.

Поэтому мы написали свою надстройку над DRF, которая имеет
1. Полную изоляцию между версиями API
1. Версионирование через заголовок `Accept`
1. Декларативную настройку сериализаторов и классов разрешений для `View` и `ViewSet`
1. Прокачанную генерацию схемы

## Установка

Добавляем пакет `restdoctor` в зависимости или ставим через pip.

Добавляем настройки в Settings:

```python
ROOT_URLCONF = 'app.urls'

INSTALLED_APPS = [
    ...,
    'rest_framework',
    'restdoctor',
]

MIDDLEWARE = [
    ...,
    'restdoctor.django.middleware.api_selector.ApiSelectorMiddleware',
]

API_FALLBACK_VERSION = 'fallback'
API_FALLBACK_FOR_APPLICATION_JSON_ONLY = False
API_DEFAULT_VERSION = 'v1'
API_DEFAULT_FORMAT = 'full'
API_PREFIXES = ('/api',)
API_FORMATS = ('full', 'compact')
API_RESOURCE_DISCRIMINATIVE_PARAM = 'view_type'
API_RESOURCE_DEFAULT = 'common'
API_RESOURCE_SET_PARAM = False
API_RESOURCE_SET_PARAM_FOR_DEFAULT = False
API_V1_URLCONF = 'api.v1_urls'
API_VERSIONS = {
    'fallback': ROOT_URLCONF,
    'v1': API_V1_URLCONF,
}
```

## Использование в проекте

Максимально наследуемся от restdoctor там, где есть выбор между `rest_framework`
и `restdoctor.rest_framework`.

```python
from restdoctor.rest_framework.serializers import ModelSerializer
from restdoctor.rest_framework.views import GenericAPIView, RetrieveAPIView, ListAPIView
from restdoctor.rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
```

### Версионирование

RestDoctor маршрутизирует вызовы по заголовку `Accept` на изолированный `UrlConf`.
1. Во-первых, это означает, что без корректного заголовка `Accept` ручки API могут быть недоступны и отдавать 404.
1. А во-вторых, в приложении может быть несколько различных версий API, которые не будут "видеть" друг друга.

Общий формат заголовка следующий:

```
application/vnd.{vendor}.{version}[-{resource}][.{format}][+json]
```

Где vendor задается на уровне приложения параметром `API_VENDOR_STRING`, список версий и сопоставление их UrlConf'ам
определяется параметром `API_VERSIONS`.

Саму маршрутизацию для входящего запроса проводит middleware `ApiSelectorMiddleware`, которую надо включить в
настройках.

```python
ROOT_URLCONF = 'app.urls'

MIDDLEWARE = [
    ...,
    'restdoctor.django.middleware.api_selector.ApiSelectorMiddleware',
]

API_V1_URLCONF = 'api.v1.urls'

API_VENDOR_STRING = 'RestDoctor'

API_FALLBACK_VERSION = 'fallback'
API_DEFAULT_VERSION = 'v1'
API_VERSIONS = {
    API_FALLBACK_VERSION: ROOT_URLCONF,
    API_DEFAULT_VERSION: API_V1_URLCONF,
}
```

Маршрутизация по `API_VERSIONS` срабатывает, если Accept начинается с `application/vnd.{vendor}`,
если не указана версия, то берется `API_DEFAULT_VERSION`. Если Accept не содержит корректной vendor-строки, то
выбирается `API_FALLBACK_VERSION`.

Версия может быть указана в формате `{version}-{resource}`, тогда `ResourceViewSet` будет использовать эту информацию
для выбора `ViewSet`.

Кроме того, может быть дополнительно указан `{format}` для выбора формата ответа, по факту выбор сериализатора в
`SerializerClassMapApiView`.

В случае успешного определения версии и параметров API из заголовка Accept, middleware выбирает для дальнейшей обработки
запроса конкретный UrlConf и добавляет к объекту `request` атрибут `api_params`.


### Формат ответа API

Нашим API Guide задан [формат ответа](https://github.com/best-doctor/guides/blob/master/guides/api_guide.md#%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82-%D0%B7%D0%B0%D0%BF%D1%80%D0%BE%D1%81%D0%B0-%D0%B8-%D0%BE%D1%82%D0%B2%D0%B5%D1%82%D0%B0), за который отвечает RestDoctorRenderer
(`restdoctor.rest_framework.renderers.RestDoctorRenderer`). Включается он только для запросов, содержащих атрибут
`api_params`, и работает этот механизм через `content_negotiation_class` заданный в базовом для View и ViewSet
миксине NegotiatedMixin (`restdoctor.rest_framework.mixins.NegotiatedMixin`).


### SerializerClassMapApiView

DRF позволяет достаточно компактно определять `ModelSeraizlier` + `ModelViewSet`, однако оставляет достаточно много
свободы в одних местах, не предоставляя ее в других.

Например, можно переопределить `serializer_class` в классе ViewSet'а, либо определять его динамически через
`ViewSet.get_serializer_class`, однако нельзя переопределять сериализаторы отдельно для запроса, отдельно для ответа.
Т.е. нельзя задать отдельный сериализатор для `update`, используя сериализатор для `retrieve` для возврата измененной
сущности.

`SerializerClassMapApiView` дает возможность декларативно задавать сериализаторы для различных action, отдельно для
request и response.

Поддержка на уровне базовых миксинов для ViewSet'ов позволяет прозрачно заменить, например,
`ReadOnlyModelViewSet` в импортах с `rest_framework.viewsets` на `restdoctor.rest_framework.viewsets`.


#### serializer_class_map

`SerializerClassMapApiView` позволяет задавать сериализаторы для разных action'ов и форматов ответа отдельно для
request и response фазы обработки запроса.

```python
from restdoctor.rest_framework.viewsets import ModelViewSet

from app.api.serializers import (
    MyDefaultSerializer, MyCompactSerializer, MyAntoherSerializer,
    MyCreateSerializer, MyUpdateSerializer,
)


class MyApiView(SerializerClassMapApiView):
    """Пример работы с serializer_class_map."""

    serializer_class_map = {
        'default': MyDefaultSerializer,
        'default.compact': MyCompactSerializer,
         'create': {
            'request': MyCreateSerializer,
         },
         'update': {
            'request': MyUpdateSerializer,
         },
         'list': {
            'response.another_format': MyAnotherSerializer,
        }
    }

```

В этом примере мы задаем `MyDefaultSerializer` как базовый для ViewSet. Но для `create` и `update` action
переопределяем сериализаторы для обработки request'а.

Кроме того, мы определили сериализатор для `compact` формата и отдельно для `list` action для `another_format`.


#### permission_classes_map

По аналогии с `serializer_class_map` для декларативного задания разных наборов `permission_classes` на разных action'ах
можно определить `permission_classes_map`:

```python
from restdoctor.rest_framework.viewsets import ModelViewSet

from app.api.permissions import PermissionA, PermissionB


class MyViewSet(ModelViewSet):
    permission_classes_map = {
        'default': [PermissionA],
        'retrieve': [PermissionB],
    }
```

#### Замечание про action

В DRF action появляется во время регистрации `ViewSet` с помощью `Router`. При этом для разделения list/detail ресурсов
используются разные наборы `action_maps`:

```
list_action_map = {'get': 'list', 'post': 'create'}
detail_action_map = {'get': 'retrieve', 'put': 'update'}
```

Django-механизмы роутинга создают функцию-обработчик, которая инстанцирует View/ViewSet с нужными параметрами.
При этом один и тот же класс `ViewSet` будет присутствовать в UrlConf в двух экземплярах с разными `action_map`.
Во время обработки запроса по HTTP методу будет определен action и вызван соответствующий метод экземпляра `ViewSet`.
И во время обработки запроса у `ViewSet` всегда задан `self.action`.

Однако это не так для `View`, поэтому в `SerializerClassMapApiView` добавлен атрибут `action`, на который завязывается
поиск сериализатора в `serializer_class_map`.


### Миксины и ModelViewSet

Миксины задают базовые операции `ModelViewSet` для `'list'`, `'retrieve'`, `'create'`, `'update'`, `'destroy'` action'ов.


От DRF-версий они отличаются в основном тем, что используют `SerializerClassMapApiView.get_request_serializer` и
`SerializerClassMapApiView.get_response_serializer` вместо `View.get_serializer`.


#### ListModelMixin

Определяет обработчик для `list` action. Определяет метод `get_collection`:

```python
class ListModelMixin(BaseListModelMixin):
    def list(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        queryset = self.get_collection()
        ...

    def get_collection(self, request_serializer: BaseSerializer) -> typing.Union[typing.List, QuerySet]:
        return self.filter_queryset(self.get_queryset())
```

Т.е. можно использовать `ListModelMixin` для работы с любыми коллекциями, а не только моделями, надо только
переопределить `ViewSet.get_collection`. При этом, если задан сериализатор для `list`, то он будет использован
для query-параметров, что позволит получить эти параметры и использовать дополнительно к filterset'у.


#### ListModelViewSet

Задан только обработчик для `list` action.


#### ReadOnlyModelViewSet

Заданы обработчики для `list` и `retrieve` action'ов.


#### CreateUpdateReadModelViewSet

Заданы обработчики для `list`, `retrieve`, `create`, `update` action'ов.


#### ModelViewSet

Полный набор action'ов: `list`, `retrieve`, `create`, `update`, `destroy`.
