# Front

This is a Nuxt application serving all the front-end pages.

## Communication with API

It is recommended to call the API directly through the `$axios` instance
provided by Nuxt, using an absolute URL without the domain name. For example if
you want to know the user's current authentication status:

```js
const user = await $axios.$get("/back/api/me/");
```

Doing so will make sure that the call works both on server-side and client-side
(as we're working with a SSR app here).
