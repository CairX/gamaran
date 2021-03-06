# mustache-py
Mustache template parser inspired by [handlebarsjs](http://handlebarsjs.com/ "handlebarsjs").

## Usage
* [Variables](#variables)
	* [Variable Escaping](#variable-escaping)
* [Each](#each)
	* [Each else](#each-else)
	* [Each this](#each-this)
	* [Each @index](#each-index)
	* [Each @key](#each-key)
* [With](#with)
	* [With else](#with-else)
* [If / Unless](#if--unless)
	* [If else](#if-else)
* [Comments](#comments)

### Variables
Access to data is done through the key names **{{name}}** based on level of context.

**Data**
```json
{
	"title": "The best title",
	"content": "Massive body of text that explains everything."
}
```

**Template**
```html
<h1>{{title}}</h1>
<p>{{content}}</p>
```

**Result**
```html
<h1>The best title</h1>
<p>Massive body of text that explains everything.</p>
```

#### Variable Escaping
Variables are HTML escaped by default. To access the data unescaped use triple curly brackets.

**Data**
```json
{
	"title": "<h1>The best title</h1>",
	"content": "<p>Massive body of text that explains everything.</p>"
}
```

**Template**
```html
{{title}}
{{{content}}}
```

**Result**
```html
&lt;h1&gt;The best title&lt;/h1&gt;
<p>Massive body of text that explains everything.</p>
```

### Each
**Data**
```json
{
	"articles": [
		{
			"title": "The best title",
			"content": "Massive body of text that explains everything."
		}, {
			"title": "Another title",
			"content": "Well written text."
		}, {
			"title": "Again?",
			"content": "Sometimes twice is just not enough."
		}
	]
}
```

**Template**
```html
{#each articles}
	<article>
		<h1>{{title}}</h1>
		<p>{{content}}</p>
	</article>
{/each}
```

**Result**
```html
<article>
	<h1>The best title</h1>
	<p>Massive body of text that explains everything.</p>
</article>
<article>
	<h1>Another title</h1>
	<p>Well written text.</p>
</article>
<article>
	<h1>Again?</h1>
	<p>Sometimes twice is just not enough.</p>
</article>
```

#### Each else
**Data**
```json
{
	"articles": []
}
```

**Template**
```html
{#each articles}
	<article>
		<h1>{{title}}</h1>
		<p>{{content}}</p>
	</article>
{else}
	<p>No articles to view.</p>
{/each}
```

**Result**
```html
<p>No articles to view.</p>
```

#### Each this
**Data**
```json
{
	"colors": [
		"Red",
		"Yellow"
		"Green",
		"Blue",
		"Purple"
	]
}
```

**Template**
```html
<ul>
{#each articles}
	<li>{{this}}</li>
{/each}
</ul>
```

**Result**
```html
<ul>
	<li>Red</li>
	<li>Yellow</li>
	<li>Green</li>
	<li>Blue</li>
	<li>Purple</li>
</ul>
```

#### Each @index
**Data**
```json
{
	"colors": [
		"Red",
		"Yellow"
		"Green",
		"Blue",
		"Purple"
	]
}
```

**Template**
```html
{#each articles}
	<p>{{@index}} {{this}}</p>
{/each}
```

**Result**
```html
<p>1. Red</p>
<p>2. Yellow</p>
<p>3. Green</p>
<p>4. Blue</p>
<p>5. Purple</p>
```

#### Each @key
**Data**
```json
{
	"article": {
		"title": "The best title",
		"content": "Massive body of text that explains everything."
	}
}
```

**Template**
```html
<dl>
{{#each article}}
	<dt>{{@key}}:</dt>
	<dd>{{this}}</dd>
{{/each}}
</dl>
```

**Result**
```html
<dl>
	<dt>title:</dt>
	<dd>The best title</dd>
	<dt>content:</dt>
	<dd>Massive body of text that explains everything.</dd>
</dl>
```

### With
**Data**
```json
{
	"article": {
		"title": "The best title",
		"content": "Massive body of text that explains everything."
	}
}
```

**Template**
```html

{{#with article}}
	<h1>{{title}}</h1>
	<p>{{content}}</p>
{{/with}}
```

**Result**
```html
<h1>The best title</h1>
<p>Massive body of text that explains everything.</p>
```

#### With else
**Data**
```json
{
	"article": {}
}
```

**Template**
```html
{#with article}
	<article>
		<h1>{{title}}</h1>
		<p>{{content}}</p>
	</article>
{else}
	<p>No articles to view.</p>
{/each}
```

**Result**
```html
<p>No articles to view.</p>
```

### If / Unless
**Data**
```json
{
	"title": "The best title",
	"content": "Massive body of text that explains everything."
}
```

**Template**
```html
<h1>{{title}}</h1>
{{#if content}}
	<p>{{content}}</p>
{{/if}}
```

**Result**
```html
<h1>The best title</h1>
<p>Massive body of text that explains everything.</p>
```

#### If else
**Data**
```json
{
	"title": "The best title"
}
```

**Template**
```html
<h1>{{title}}</h1>
{{#if content}}
	<p>{{content}}</p>
{{else}}
	<p>No content.</p>
{{/if}}
```

**Result**
```html
<h1>The best title</h1>
<p>No content.</p>
```

### Comments
**Template**
```html
{{! This comment will not be in the output. }}
{{!-- Any comments that must contain }} or other parser tokens should use this comment style. --}}
<h1>Title</h1>
```

**Result**
```html
<h1>Title</h1>
```
