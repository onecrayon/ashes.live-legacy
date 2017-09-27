<template>
	<div class="editor">
		<div class="form-field">
			<label :for="fieldName.toLowerCase() + '-editor-field'">{{ fieldName }}</label>
			<textarea v-model="field" :id="fieldName.toLowerCase() + '-editor-field'"></textarea>

			<p class="help-text">
				<em>Supports card codes:</em><br>
				<code>[[Anchornaut]]</code> <i class="fa fa-arrow-right"></i> <span v-html="parseCardCodes('[[Anchornaut]]')"></span><br>
				<code>[[main]] - [[charm:class]]</code> <i class="fa fa-arrow-right"></i> <span v-html="parseCardCodes('[[main]] - [[charm:class]]')"></span><br>
				<a href="#" @click.prevent="showAll = !showAll">Toggle full list</a>
			</p>
		</div>

		<div v-if="showAll">
			<hr>
			<table class="help-text" cellpadding="0" cellspacing="0"><tbody>
				<tr v-for="code of exampleCardCodes" :key="code">
					<td><code>{{ code }}</code></td>
					<td v-html="parseCardCodes(code)"></td>
				</tr>
			</tbody></table>
		</div>
	</div>
</template>

<script>
	import {parseCardCodes} from 'app/utils'
	import {reduce} from 'lodash'

	export default {
		props: ['field', 'fieldName'],
		data: function () {
			return {
				showAll: false,
				exampleCardCodes: reduce(globals.diceData, (result, value) => {
					result.push('[[' + value + ']]', '[[' + value + ':class]]')
					return result
				}, [
					'[[Hammer Knight]]',
					'[[main]]',
					'[[side]]',
					'[[exhaust]]',
					'[[discard]]',
					'[[basic]]'
				])
			}
		},
		methods: {
			parseCardCodes
		}
	}
</script>

