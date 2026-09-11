### Excel component requirements

The requirement is to create a page where excel component will be used, this will allow the users to upload a excel.
The data should be rendered in the table format and the user should be able to perform the following actions:
1. Upload an Excel file (.xlsx or .xls format).
2. Display the data from the uploaded Excel file in a table format.
3. Allow users to edit the data directly in the table.
4. Provide functionality to add new rows to the table.
5. Allow users to delete existing rows from the table.
6. Provide a button to download the modified data back to an Excel file.
7. Ensure that the table supports basic data validation (e.g., required fields, data types).

#### Technical Requirements:
- Use Quarkus web bundler 
- Use react , react-dom 
- Use ddan.github.io/react-spreadsheet .
- Use gradle build tool

#### Quarkus Web Bundler Configuration:
Create full-stack web apps and components with this Quarkus extension. It offers zero-configuration bundling and minification (with source-map) for your web app scripts (JS, JSX, TS, TSX), dependencies (jQuery, htmx, Bootstrap, Lit etc.), and styles (CSS, SCSS, SASS).

No need to install NodeJs manually, it relies on a Java native binding of Deno and esbuild. For libraries, all the NPM catalog is accessible through Maven or Gradle dependencies.

1. [ ] Easy to set up
2. [ ] Production build
3. [ ] Awesome Dev experience with browser live-reload
4. [ ] Integrated with NPM dependencies through mvnpm or WebJars.
5. [ ] Build-time index.html rendering with bundled scripts and styles
6. [ ] Pre-configured TailwindCSS 4+ integration
7. [ ] Server Side Qute Components (Qute template + Script + Style)

>> The Web Bundler has been pre-configured to reduce the complexity of web bundling. You don’t need to know all the concepts of web bundling (entry-points, loaders, …) to use this extension, it has been pre-configured with sensible defaults that you may change if needed.

### Installation
-----



If you want to use this extension, you need to add the io.quarkiverse.web-bundler:quarkus-web-bundler extension first to your build file.

For instance, with Maven, add the following dependency to your POM file:
```xml
<dependency>
    <groupId>io.quarkiverse.web-bundler</groupId>
    <artifactId>quarkus-web-bundler</artifactId>
    <version>2.3.4</version>
</dependency>
```

With Gradle, you need to add this plugin (to allow architecture based resolution) and the dependency:

```groovy
plugins {
id("io.mvnpm.gradle.plugin.native-java-plugin") version "1.0.0"
}

```

```groovy


dependencies {
implementation("io.quarkiverse.web-bundler:quarkus-web-bundler:2.3.4")
}
```


Plug the bundle in your index.html template (More info on this):

src/main/resources/web/index.html
```html

<html>
<head>
  ...
  {#bundle /}
</head>
</html>
```

Will compile into something looking like this:

```html

<html>
<head>
      ...
      <script type="text/javascript" src="/static/app-XKHKUJNQ.js"></script>
      <link rel="stylesheet" media="screen" href="/static/app-TLNDARM3.css">
</head>
</html>
```

You are all set, enjoy web live coding!

By default {#bundle /} inserts both script and style tags for app, this is configurable.
Adding Scripts, Styles and Web Dependencies
Add your web resources in src/main/resources/web:

App scripts (js, ts, jsx, tsx, …), styles (css, scss, sass) and assets (svg, jpg, gif, png, …), to be bundled and served under http://localhost:8080/static/bundle/

public/**: Any public file to be served without change under http://localhost:8080/..

Add Web Dependencies to the pom and import them (scripts and styles):

`web/script.js`

```js

import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.css';

$('.hello').innerText('Hello');
```

If you don’t import a Web Dependency, it won’t be bundled (dead code elimination).

### Quarkus logo Web Bundler - Main Concepts

#### How it works
It’s really simple, the web bundler:

#### Web Bundler schema

Takes/watches your web resources and Web Dependencies.

Bundles it with the supersonic esbuild compiler (scss are also compiled if needed) and serves them.

Make it easy to create pages (.html) with the bundle scripts and styles using Qute or any other template engine.

#### Web Dependencies
Once added in the pom.xml the dependencies are directly available through import from the scripts and styles:

`app.js`
```js

import $ from 'jquery';

$('.hello').innerText('Hello');
```

Imported dependencies scripts and styles will be bundled.

Only imported dependencies (scripts and styles) will be bundled, dead code will be eliminated during the build.



### Quarkus logo Web Bundler - Advanced Guides

#### Web Root
The Web Root is src/main/resources/web, this is where the Web Bundler will look for stuff to bundle and serve.

#### Static files
There are 2 ways to add static files (fonts, images, music, video, …) to your app:

Files in src/main/resources/web/public/** will be served statically under http://localhost:8080/.

Other files imported from scripts or styles will be bundled and processed by the configured loaders (see How is it bundled (Loaders)) allowing different options (like embedding them as data-url).

For convenience, everything under /static is excluded (marked as external) from the bundling by default. This allows to reference static files from scripts or styles without errors (e.g. import '/static/foo.png';).

#### HTML templates rendering
The Web-Bundler is natively integrated with Qute Template Engine to render html templates at build-time (this won’t affect runtime). This way you may create SPA out of the box. For this, just provide an index.html file (or any other .html file) in the src/main/resources/web directory.

Combined with the {#bundle /} tag, this file will be rendered with the scripts and styles tags to include in your html template. This file will be served as the default index file (e.g. http://localhost:8080/).

You can use the Qute config: namespace, it will be evaluated a build-time (runtime config will be ignored).
Why is the directory different from other Qute app (i.e. src/main/resources/templates/)?

When used in src/main/resources/web the rendering is happening at build time (and doesn’t require Qute at runtime). It only offers partial support, so you won’t be able to access any Qute runtime data in this file. If you want to render data (for example in a server-side rendering app with htmx), you should add the Qute Web extension (or Renarde extension for MVC with Qute) and use src/main/resources/templates/ directory instead. The {#bundle /} tag will also work with Quarkus Qute.

#### Web Live-Coding
The Web Bundler enable browser live coding for development.

This is done through:

* a custom project sources watcher in Quarkus Dev
* a small injected script (only in dev-mode). This script will listen for changes from the server.

In this mode when you change the sources, the page will automatically be:

* hot-reloaded (no refresh) when a style is modified (css, scss).
* refreshed when a js, template or java file is modified.

When web live coding is enabled, to allow it to work properly, minification and bundle hashes are disabled in dev-mode.

This can be disabled through browser-live-reload config.

> After a deployment/bundling error, you need to manually refresh the page to get back in live-reload mode.

#### Bundling
By default, directory src/main/resources/web/ is destined to contain the scripts, styles and possibly assets for your app. It will be bundled and served into /static/bundle/app-[hash].[ext]. (see Entry-Points for more options).

Importing Web Dependencies
Once added in the pom.xml, the web dependencies can be imported and used with the ESM import syntax, they will automatically be bundled.

Web Dependencies (script and styles) need to be imported in order to be bundled, dead code will be eliminated during the build.
`web/script.js`
```js

import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.css';

$('.hello').innerText('Hello');
```

Styles can be also be imported from a scss file:

`web/style.scss`

```js
@import "bootstrap/dist/scss/bootstrap.scss";
```

#### What is bundled
##### Indexing
Only what’s imported will be part of the resulting bundle, to make it easy, the Web Bundler will automatically generate an index importing all the files found in an entry-point directory.

Of course, you can also provide this index manually (named index.js,ts,jsx,tsx) and choose what to import. Example:

`src/main/resources/web/index.js`
```js

import './my-script.js'
import './my-style.scss'
import './example.png'
```

###### Entry-Points
You may configure different entry-points (to generate different bundles):

`src/main/resources/application.properties`
```properties

quarkus.web-bundler.bundle.page-1=true
quarkus.web-bundler.bundle.page-2=true
```

* Bundle src/main/resources/web/page-1/… into /static/bundle/page-1-[hash].[ext]
* Bundle src/main/resources/web/page-2/… into /static/bundle/page-2-[hash].[ext]
* 
or customize the directory name and bundled file name (and possibly merge multiple directories into one bundle):

`src/main/resources/application.properties`
```properties

quarkus.web-bundler.bundle.foo=true
quarkus.web-bundler.bundle.bar=true
quarkus.web-bundler.bundle.bar.key=my-key
quarkus.web-bundler.bundle.bar.dir=my-dir
quarkus.web-bundler.bundle.baz=true
quarkus.web-bundler.bundle.baz.key=foo
```

Bundle src/main/resources/web/foo/…
and 
src/main/resources/web/baz/… together into /static/bundle/foo-[hash].[ext]
Bundle src/main/resources/web/my-dir/… into /static/bundle/my-key-[hash].[ext]

> Scripts and styles located at the root of the web directory (e.g. src/main/resources/web/style.css) are automatically bundled as part of the default app entry point, as if they were in web/app/. This makes it easy to get started without creating the web/app/ subdirectory.

> As soon as one or more custom entry-points are configured:
> * Scripts and styles located at the root of the web directory will not be bundled. To keep things organized, move them to the web/app/ directory (or remove them if unnecessary).
> * When multiple output entry points exist, shared code and web dependencies are extracted into a separate file which is auto-imported in {#bundle /}. This ensures that if a user navigates from one page to another, they don’t need to download all the JavaScript for the second page again, as shared parts are already cached by the browser.

How is it bundled (Loaders)
Bases on the files extensions, the Web Bundler will use pre-configured loaders to bundle them. For scripts and styles, the default configuration should be enough.

For other assets (svg, gif, png, jpg, ttf, …) imported from your scripts and styles using their relative path, you may choose the loader based on the file extension allowing different options (e.g. serving, embedding the file as data-url, binary, base64, …). By default, they will automatically be copied and served using the file loader.

For example, url('./example.png') in a style or import example from './example.png'; in a script will be processed, the file will be copied with a static name and the path will be replaced by the new file static path (e.g. /static/bundle/assets/example-QH383.png). The example variable will contain the public path to this file to be used in a component img src for example.

For convenience, when using a file located in the static directory (e.g. url('/static/example.png'), the path will not be processed because all files under /static/** are marked as external (to be ignored from the bundling). Since /static/example.png will be served by Quarkus (See Static files), it is ok.
SCSS, SASS
You can use scss or sass files out of the box. Local import are supported. Importing partials is also supported begin with _ (as in _code.scss imported with @import 'code';).

### Web Dependencies
The Web Bundler is integrated with NPM dependencies through MVNPM (default) (default) or WebJars. Once added in the pom.xml the dependencies are directly available through import from the scripts and styles.

Using the Web Bundler, Web Dependencies are bundled, there is not point for the jars to be packaged in the resulting app. Web Dependencies with provided scope (or compileOnly with Gradle) will not be packaged in the resulting app.

> INFO: By default, the Web Bundler will fail at build time if it detects non compile only Web Dependencies. You can configure a flag to allow them but keep in mind that they will be served by Quarkus.

If you don’t import a Web Dependency from an entry-point (Indexing), it won’t be bundled (dead code elimination).
MVNPM (default)
mvnpm (Maven NPM) is a maven repository facade on top of the NPM Registry.

Lookup for packages on https://mvnpm.org or https://www.npmjs.com/ then add them as web dependencies to your pom.xml:

`pom.xml`
```xml
<dependencies>
...
    <dependency>
    <groupId>org.mvnpm</groupId>
    <artifactId>jquery</artifactId>
    <version>3.7.0</version>
    <scope>provided</scope>
    </dependency>
...    
</dependencies>
```

* use org.mvnpm or org.mvnpm.at.something for @something/dep
* All dependencies published on NPM are available
* Any published NPM version for your dependency
* Use provided scope to avoid having the dependency packaged in the target application

If a package or a version in not yet available in Maven Central:

* You may use the mvnpm.org website to synchronize new versions with Maven Central (Click on the Maven Central icon)
* If configured with the mvnpm repository, when requesting a dependency, it will inspect the registry to see if it exists and if it does, convert it to a Maven dependency and publish it to Maven Central so that future developers (and CI) won’t need the repository.

Configure the mvnpm-repo profile in your ~/.m2/settings.xml: .settings.xml

```xml
<settings>
    <profiles>
        <profile>
            <id>mvnpm-repo</id>
            <repositories>
                <repository>
                    <id>central</id>
                    <name>central</name>
                    <url>https://repo.maven.apache.org/maven2</url>
                </repository>
                <repository>
                    <snapshots>
                        <enabled>false</enabled>
                    </snapshots>
                    <id>mvnpm.org</id>
                    <name>mvnpm</name>
                    <url>https://repo.mvnpm.org/maven2</url>
                </repository>
            </repositories>
        </profile>
    </profiles>
</settings>
```

> I only use -Pmvnpm-repo when locking my project or updating mvnpm versions.

> In case of web dependencies versions conflicts, you can set the version to use for this dependency in the project dependencyManagement (even when using the locker).

#### Browser live-reload
Browser live reload is enabled by default:

auto-inject a live-reload script in the bundle to watch for changes through sse (server-sent event)

supersonic in-page replace for css/scss changes

supersonic page refresh for javascript changes

watch other Quarkus files such as html, java, … (unless there is an error in which case a new request is needed)

This is enabled by default. To disable:

```properties
quarkus.web-bundler.browser-live-reload=false
```

When browser-live-reload is enabled:

bundle files will be fixed (no hashes, i.e. app.js)

minification is disabled

Node Modules for bundling
To deal with Web Dependencies, the Web Bundler manages a node_modules directory. The default location for it is the project directory. Don’t forget to add the node_modules/ to the .gitignore, the IDE will look recursively in parent directories for imports and the Web Bundler too.

Locking dependencies
As the NPM ecosystem is over-using version ranges for dependencies, just a few npm dependencies can lead to a big amount of poms to download in order to get the right versions for your project. This leads to long lasting minutes of downloading poms when cloning or during CI. To solve this problem and also to make your build reproducible it is highly recommended to lock your web dependencies versions. This way it will be long only the first time and then it will be fast and reproducible.

Locking with Maven (mvnpm Locker Maven Plugin)
As Maven doesn’t provide a native version locking system, the mvnpm team has implemented a way to easily generate and use a locking pom.xml (BOM). The locker Maven Plugin will create a version locker BOM for your org.mvnpm and org.webjars dependencies. It is essential as NPM dependencies are over using ranges. After the locking, the quantity of files to download is considerably reduced (better for reproducibility, contributors and CI).

It is easy to set up and update, here is the documentation.

Locking with Gradle
Gradle provides a native version locking system, to install it, add this:


`build.gradle`
```groovy

dependencyLocking {
lockAllConfigurations()
}
```

Then run gradle dependencies --write-locks to generate the lockfile.

WebJars
Adding new dependencies or recent versions has to be done manually from their website.
WebJars are client-side web libraries (e.g. jQuery & Bootstrap) packaged into JAR (Java Archive) files. You can browse the repository from the website.

`pom.xml`
```xml
<dependency>
<groupId>org.webjars.npm</groupId>
<artifactId>jquery</artifactId>
<version>3.7.0</version>
<scope>provided</scope>
</dependency>
```

### Bundle Paths
After the bundling is done, the bundle files will be served by Quarkus under {quarkus.http.root-path}/static/bundle/… by default (Config Reference).

This may also be configured with an external URL (e.g. 'https://my.cdn.org/'), in which case, Bundle files will NOT be served by Quarkus and all resolved paths in the bundle and mapping will automatically point to this url (a CDN for example).

In production, it is a good practise to have a hash inserted in the scripts and styles file names (E.g.: app-XKHKUJNQ.js) to differentiate builds (make them static). This way they can be cached without a risk of missing the most recent builds. This option is enabled by default in production.

To make it easy there are several ways to resolve the bundle files public paths from the templates and the code.

{#bundle /} tag
From any Qute template you can use the {#bundle /} tag to help insert the bundled scripts and styles in your html page. examples:

```html

{#bundle /}
Output:
<script type="text/javascript" src="/static/bundle/app-[hash].js"></script>
<link rel="stylesheet" media="screen" href="/static/bundle/app-[hash].css">

{#bundle key="components"/}
Output:
<script type="text/javascript" src="/static/bundle/components-[hash].js"></script>
<link rel="stylesheet" media="screen" href="/static/bundle/components-[hash].css">

{#bundle tag="script"/}
Output:
<script type="text/javascript" src="/static/bundle/app-[hash].js"></script>

{#bundle tag="style"/}
Output:
<link rel="stylesheet" media="screen" href="/static/bundle/app-[hash].css">

{#bundle key="components" tag="script"/}
Output:
<script type="text/javascript" src="/static/bundle/components-[hash].js"></script>
```
### Bundle Import Map

The {#bundleImportMap /} tag generates an import map that allows you to import modules directly from your bundled application within HTML <script type="module"> blocks.

When used together with {#bundle /}, the {#bundleImportMap /} tag automatically creates an import map linking your bundle exports (e.g. 'app' → /static/bundle/app-3HNF28.js) to the correct bundled file path which is changing on every build with a different hash. This makes it possible to use ES module imports in HTML.

Example
`web/app.js`
```js
export const name = "import!";
```

`index.html`
```html
<html>
<head>

{#bundle /}
{#bundleImportMap /}

<script type="module">
  import { name } from 'app';
  alert(`Hello ${name}`);
</script>

</head>
</html>
```
Inject Bundle bean
This bean can be injected in the code:

```java

@Inject
Bundle bundle;

...

System.out.println(bundle.script("app"));
System.out.println(bundle.style("app"));
```

or in a Qute template:
```html
{inject:bundle.script("app")}
{inject:bundle.style("app")}
```


```asciidoc

= Quarkus image:logo.svg[width=25em] Web Bundler - Integrations

include::./_includes/attributes.adoc[]

[#tailwindcss]
== TailwindCSS

We added a Web Bundler + https://tailwindcss.com/docs/styling-with-utility-classes[TailwindCSS 4+, window="_blank"] extension which makes it very easy to use Tailwind with Quarkus (and https://iamroq.com/[Roq, window="_blank"]).

Tailwind CSS lets you rapidly build modern websites by applying utility classes directly in your HTML or through your CSS.

=== Installation

If you want to use this extension, you need to add the `io.quarkiverse.web-bundler:quarkus-web-bundler-tailwindcss` extension first to your build file.

For instance, with Maven, add the following dependency to your POM file:

[source,xml,subs=attributes+]
----
<dependency>
    <groupId>io.quarkiverse.web-bundler</groupId>
    <artifactId>quarkus-web-bundler-tailwindcss</artifactId>
    <version>{project-version}</version>
</dependency>
----

With Gradle, you need to add this plugin (to allow architecture based resolution) and the dependency:
[source,kotlin,subs=attributes+]
----
plugins {
  id("io.mvnpm.gradle.plugin.native-java-plugin") version "1.0.0"
}

...

dependencies {
    implementation("io.quarkiverse.web-bundler:quarkus-web-bundler-tailwindcss:{project-version}")
}
----

=== Usage

There is no need to add the TailwindCSS mvnpm dependency in your project.

Then in your web directory:
[source,css]
.web/style.css
----
@import "tailwindcss";
----

*Start using Tailwind in your HTML*:

For example with Qute Web, start using Tailwind’s utility classes to style your content:

[source,css]
.src/main/resources/templates/pub/index.html
----
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{#bundle /}
</head>
<body>
<h1 class="text-3xl font-bold underline">
Hello world!
</h1>
</body>
</html>
----

=== Configuration

TailwindCSS is pre-configured to scan all Qute templates in your project and jars (and in Roq files) looking for class candidates in order to optimize your output css.

It is possible to manually configure the pattern for scanning via the Quarkus configuration:
include::_includes/quarkus-web-bundler-tailwindcss.adoc[leveloffset=+1, opts=optional]

WARNING: The `@source` path is resolved from the bundling directory (`target`), not relative to your source file, which can make referencing source files tricky. If the default setup and pattern do not meet your needs, https://github.com/quarkiverse/quarkus-web-bundler/issues/366[vote up this issue].

=== Splitting Styles

You can split your Tailwind CSS by importing files from your main stylesheet:

[source,css]
.web/style.css
----
@import "tailwindcss";
@import "./_theme.css";
----

Prefix imported files with `_` so they aren’t treated as root bundles, and don’t include `@import "tailwindcss";` again:

[source,css]
.web/_theme.css
----
@theme {
  --color-mint-500: oklch(0.72 0.11 178);
}
----

=== Tailwind Plugins

It is possible to use Tailwind plugins (DaisyUI, Flowbite, ...). Add the mvnpm dependency in your project (as provided) and then use the `@plugin` in your Tailwind css file.

==== Tailwind Typography plugin (styling rich text content)

The https://github.com/tailwindlabs/tailwindcss-typography[Tailwind Typography, window="_blank"] plugin *is pre-installed* because it’s essential for styling rich text content, allowing you to use it without adding extra dependencies.:

.web/style.css
[source,css]
----
@import "tailwindcss";
@plugin "@tailwindcss/typography";
----

Then in your html templates:
[source,html]
----
<article class="prose">
  <h1>Hello World</h1>
  <p>This text is styled using Tailwind Typography.</p>
</article>
----

[#svelte]
== Svelte

We added a Web Bundler + https://svelte.dev/[Svelte, window="_blank"] extension which makes it very easy to use Svelte with Quarkus.

Svelte is a UI framework that uses a compiler to let you write breathtakingly concise javascript components that do minimal work in the browser, using languages you already know — HTML, CSS and JavaScript. It may be used to create Javascript components for Qute for example.

=== Installation

If you want to use this extension, you need to add the `io.quarkiverse.web-bundler:quarkus-web-bundler-svelte` extension first to your build file.

For instance, with Maven, add the following dependency to your POM file:

[source,xml,subs=attributes+]
----
<dependency>
    <groupId>io.quarkiverse.web-bundler</groupId>
    <artifactId>quarkus-web-bundler-svelte</artifactId>
    <version>{project-version}</version>
</dependency>
----

With Gradle, you need to add this plugin (to allow architecture based resolution) and the dependency:
[source,kotlin,subs=attributes+]
----
plugins {
  id("io.mvnpm.gradle.plugin.native-java-plugin") version "1.0.0"
}

...

dependencies {
    implementation("io.quarkiverse.web-bundler:quarkus-web-bundler-svelte:{project-version}")
}
----

=== Usage

There is no need to add the Svelte mvnpm dependency in your project when using custom elements (configurable).

In your web directory:
[source,sveltehtml]
.web/App.svelte
----
<svelte:options customElement="my-component" />
<script>
	let count = $state(0);

	function increment() {
		count += 1;
	}
</script>

<button onclick={increment}>
	Clicked {count}
	{count === 1 ? 'time' : 'times'}
</button>
----

=== Configuration

include::_includes/quarkus-web-bundler-svelte.adoc[leveloffset=+1, opts=optional]

[#qute-components]
== Server-Side Qute Components

When you need to include custom scripts or styles in your Qute tags, Server-Side Qute Components provides an elegant solution.

IMPORTANT: This requires `quarkus-qute` or `quarkus-qute-web` in the project (and this is not made to be used with the build-time template rendering).

To enable server-side components, add this in the `application.properties`:
[source,properties]
----
quarkus.web-bundler.bundle.components=true
quarkus.web-bundler.bundle.components.key=app // <1>
quarkus.web-bundler.bundle.components.qute-tags=true // <2>
----
<1> use `app` to have a single merged bundle with the `app` (or remove this line to use `components` as default)
<2> activate qute-tags support (default is `false`)

Here is a nice convention to define your components: `src/main/resources/web/components/[name]/[name].{html,css,scss,js,ts,...};`. The scripts, styles and assets will be bundled, the html template will be usable as a {quarkus-guides-url}/qute-reference#user_tags[Qute tag].

Example:
- `src/main/resources/web/components/hello/hello.html`
- `src/main/resources/web/components/hello/hello.js`
- `src/main/resources/web/components/hello/hello.scss`

This way you can use `{#hello}` in your templates and the scripts & styles will be bundled.

NOTE: You may create different qute components groups to be used in different pages.

```

```asciidoc

= Quarkus image:logo.svg[width=25em] Web Bundler - Examples

include::./_includes/attributes.adoc[]

== Demos

All these demo applications use the **Web Bundler**:

=== Renarde
* **htmx-todo** — A Todo app using Renarde and Htmx  
  image:github.svg[width=16px] https://github.com/ia3andy/htmx-todo[Source, window="_blank"]
* **quarkus-blast** — A board game example with OIDC login using Renarde, Htmx, Hyperscript, and Bootstrap  
  image:github.svg[width=16px] https://github.com/ia3andy/quarkus-blast[Source, window="_blank"]
* **renotes** — A note-taking app with Markdown support using Renarde, Htmx, and Bootstrap  
  image:github.svg[width=16px] https://github.com/ia3andy/renotes[Source, window="_blank"]

=== Lit
* **todo-demo-app** — A Todo demo application using Lit and Vaadin Web Components  
  image:github.svg[width=16px] https://github.com/quarkusio/todo-demo-app[Source, window="_blank"]
* **star-rating** — A full-stack star rating web component using Lit  
  image:github.svg[width=16px] https://github.com/ia3andy/star-rating[Source, window="_blank"]

=== React
* **quarkus-bundler-react** — A minimalist SPA demo with React Bootstrap  
  image:github.svg[width=16px] https://github.com/ia3andy/quarkus-bundler-react[Source, window="_blank"]
* **quarkus-wb-patternfly-react** — A minimalist SPA demo with PatternFly React  
  image:github.svg[width=16px] https://github.com/ia3andy/quarkus-wb-patternfly-react[Source, window="_blank"]

=== jQuery
* **web-bundler-jquery** — A jQuery example with Bootstrap  
  image:github.svg[width=16px] https://github.com/ia3andy/web-bundler-jquery[Source, window="_blank"]
* **bundler-gradle-jquery** — The same example using Gradle  
  image:github.svg[width=16px] https://github.com/ia3andy/bundler-gradle-jquery[Source, window="_blank"]

== Real World

The **Web Bundler** is also used in production applications:

* **code.quarkus.io** — The Code Quarkus app generator, a React SPA  
  image:github.svg[width=16px] https://github.com/quarkusio/code.quarkus.io[Source, window="_blank"] | https://code.quarkus.io[Visit, window="_blank"]
* **mvnpm** — The mvnpm SPA built with Lit  
  image:github.svg[width=16px] https://github.com/mvnpm/mvnpm[Source, window="_blank"] | https://mvnpm.org[Visit, window="_blank"]
* **RivieraDEV-Quarkus** — The Riviera Dev Conference website built with Renarde (MVC)  
  image:github.svg[width=16px] https://github.com/FroMage/RivieraDEV-Quarkus[Source, window="_blank"] | https://rivieradev.fr[Visit, window="_blank"]
* **search.quarkus.io** — Quarkus guides search, a Lit full-stack web component  
  image:github.svg[width=16px] https://github.com/quarkusio/search.quarkus.io[Source, window="_blank"] | https://quarkus.io/guides[Visit, window="_blank"]

```

