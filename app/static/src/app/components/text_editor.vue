<template>
	<div class="editor">
		<div class="form-field full-width">
			<textarea-helpers @actOnText="modifyText"></textarea-helpers>
			<textarea ref="textarea" v-model="content" :id="fieldName.toLowerCase() + '-editor-field'" :placeholder="fieldName"></textarea>

			<p class="help-text"><em>Supports [[card codes]] and *star formatting*:</em></p>
			<p class="help-text">
				<code>[[Anchornaut]]</code> <i class="fa fa-arrow-right"></i> <card-codes content="[[Anchornaut]]"></card-codes><br>
				<code>[[main]] - [[charm:class]]</code> <i class="fa fa-arrow-right"></i> <card-codes content="[[main]] - [[charm:class]]"></card-codes><br>
				<code>*italic* - **bold**</code> <i class="fa fa-arrow-right"></i> <card-codes content="*italic* - **bold**"></card-codes>
			</p>
			<p class="help-text"><a href="#" @click.prevent="showAll = !showAll">Toggle full list</a></p>
		</div>

		<div v-if="showAll">
			<hr>
			<pre class="help-text boxed no-margin"><code>**First five:**

* [[Root Armor]]
* [[side]] - 1 [[natural:class]]
* [[Love this site! ashes.live]]
* *etc.*

> [[Skaak#1st!]] said:
> Quote text like this!</code></pre>
			<p class="text-center no-margin"><i class="fa fa-arrow-down"></i></p>
			<div class="boxed no-margin">
				<p class="help-text"><card-codes content="**First five:**"></card-codes></p>
				<ul class="help-text">
					<li><card-codes content="[[Root Armor]]"></card-codes></li>
					<li><card-codes content="[[side]] - 1 [[natural:class]]"></card-codes></li>
					<li><card-codes content="[[Love this site! ashes.live]]"></card-codes></li>
					<li><card-codes content="*etc.*"></card-codes></li>
				</ul>
				<blockquote>
					<p class="help-text">
						<card-codes content="[[Skaak#1st!]] said:"></card-codes><br>
						Quote text like this!
					</p>
				</blockquote>
			</div>
			<hr>
			<h4 class="help-text">All card codes</h4>
			<table class="help-text" cellpadding="0" cellspacing="0"><tbody>
				<tr v-for="code of exampleCardCodes" :key="code">
					<td><code>{{ code }}</code></td>
					<td><card-codes :content="code"></card-codes></td>
				</tr>
			</tbody></table>
		</div>
	</div>
</template>

<script>
	import CardCodes from 'app/components/card_codes.vue'
	import TextareaHelpers from 'app/components/textarea_helpers.vue'
	import {actOnText, globals, getFromObject} from 'app/utils'
	import {reduce} from 'lodash'

	export default {
		props: ['statePath', 'fieldName'],
		components: {
			'card-codes': CardCodes,
			'textarea-helpers': TextareaHelpers
		},
		data: function () {
			return {
				setMethod: null,
				showAll: false,
				exampleCardCodes: reduce(globals.diceData, (result, value) => {
					result.push('[[' + value + ']]', '[[' + value + ':class]]')
					return result
				}, [
					'[[Hammer Knight]]',
					'[[*Hammer Knight]]',
					'[[Skaak#1st!]]',
					'[[Link Text ashes.live]]',
					'[[*https://placekitten.com/30/30]]',
					'[[main]]',
					'[[side]]',
					'[[exhaust]]',
					'[[discard]]',
					'[[basic]]'
				])
			}
		},
		computed: {
			content: {
				get () {
					return getFromObject(this.$store.state, this.statePath)
				},
				set (value) {
					if (!this.setMethod) {
						this.setMethod = 'set' + this.statePath.replace(/(?:^|\.)([a-z])/g, (_, letter) => {
							return letter.toUpperCase()
						})
					}
					this.$store.commit(this.setMethod, value)
				}
			}
		},
		methods: {
			modifyText (actions) {
				const logic = actOnText(
					this.content,
					this.$refs.textarea.selectionStart,
					this.$refs.textarea.selectionEnd,
					actions
				)
				if (!logic) return
				this.content = logic.text
				this.$nextTick(() => {
					this.$refs.textarea.setSelectionRange(logic.start, logic.end)
				})
			},
		}
	}
</script>

