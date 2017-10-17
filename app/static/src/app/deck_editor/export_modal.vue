<template>
	<modal :show="show" @close="close">
		<h2>Export Deck</h2>

		<div class="form-field">
			<textarea v-model="deckText"></textarea>
		</div>

		<div class="text-right">
			<button class="btn btn-primary" @click="close">Done</button>
		</div>
	</modal>
</template>

<script>
	import Modal from 'app/components/modal.vue'
	import {startCase} from 'lodash'

	export default {
		components: {
			'modal': Modal
		},
		props: ['show'],
		computed: {
			deckText () {
				let text = [
					this.$store.state.deck.title || 'Untitled ' + this.$store.getters.phoenixborn.name,
					'\n\nPhoenixborn: ',
					this.$store.getters.phoenixborn.name,
					'\n\n'
				]
				let haveDice = false
				for (const die of Object.keys(this.$store.state.deck.dice)) {
					const count = this.$store.state.deck.dice[die]
					if (count) {
						haveDice = true
						text.push(count, 'x ', startCase(die), '\n')
					}
				}
				if (haveDice) {
					text.push('\n')
				}
				for (const section of this.$store.getters.deckSections) {
					text.push(section.title, '\n')
					for (const card of section.contents) {
						text.push(card.count, 'x ', card.data.name)
						if (card.data.phoenixborn) {
							text.push(' (', card.data.phoenixborn, ')')
						}
						text.push('\n')
					}
					text.push('\n')
				}
				return text.join('')
			}
		},
		methods: {
			close () {
				this.$emit('close')
			}
		}
	}
</script>

