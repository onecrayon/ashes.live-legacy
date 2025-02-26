<template>
	<modal :show="showValue" @close="close">
		<h2>Export As Text</h2>

		<div class="form-field deck-export">
			<textarea ref="textarea" @click="selectAll" v-model="deckText" readonly></textarea>
		</div>

		<ul class="export-options responsive-cols">
			<li class="col">
				<div class="onoffswitch">
					<input type="checkbox" class="onoffswitch-checkbox" id="card-count-input"
						v-model="showCardCounts">
					<label class="onoffswitch-label" for="card-count-input">
						<span class="onoffswitch-inner"></span>
						<span class="onoffswitch-switch"></span>
					</label>
				</div> Card totals
			</li>
			<li class="col">
				<div class="onoffswitch">
					<input type="checkbox" class="onoffswitch-checkbox" id="sort-type-input"
						v-model="sortByType">
					<label class="onoffswitch-label" for="sort-type-input">
						<span class="onoffswitch-inner"></span>
						<span class="onoffswitch-switch"></span>
					</label>
				</div> Sort by type
			</li>
			<li class="col">
				<div class="onoffswitch">
					<input type="checkbox" class="onoffswitch-checkbox" id="attribution-input"
						v-model="showAttribution">
					<label class="onoffswitch-label" for="attribution-input">
						<span class="onoffswitch-inner"></span>
						<span class="onoffswitch-switch"></span>
					</label>
				</div> Attribution
			</li>
		</ul>
	</modal>
</template>

<script>
	import Modal from 'app/components/modal.vue'
	import {startCase, trimEnd} from 'lodash'

	export default {
		components: {
			'modal': Modal
		},
		props: ['show'],
		data () {
			return {
				showAttribution: true,
				showCardCounts: true,
				sortByType: true
			}
		},
		computed: {
			showValue () {
				if (this.show) {
					this.$nextTick(this.selectAll)
				}
				return this.show
			},
			deckText () {
				let text = [
					this.$store.state.deck.title || this.$store.getters.untitledText,
					'\n\nPhoenixborn: ',
					this.$store.getters.phoenixborn.name,
					'\n\n'
				]
				let haveDice = false
				for (const die of Object.keys(this.$store.state.deck.dice)) {
					const count = this.$store.state.deck.dice[die]
					if (count) {
						if (!haveDice) {
							text.push('Dice:\n')
							haveDice = true
						}
						text.push(count, 'x ', startCase(die), '\n')
					}
				}
				if (haveDice) {
					text.push('\n')
				}
				if (this.$store.getters.totalCards) {
					if (!this.sortByType || this.showCardCounts) {
						text.push('Cards')
						if (this.showCardCounts) {
							text.push(' (', this.$store.getters.totalCards, '/30)')
						}
						text.push(':\n')
						if (this.sortByType) {
							text.push('\n')
						}
					}
					let cardsOnly = []
					let conjurations = null
					const pushCards = (cards) => {
						for (const card of cards) {
							text.push(card.count, 'x ', card.data.name)
							if (card.data.phoenixborn) {
								text.push(' (', card.data.phoenixborn, ')')
							}
							text.push('\n')
						}
					}
					for (const section of this.$store.getters.deckSections) {
						if (this.sortByType) {
							text.push(section.title)
							if (this.showCardCounts && section.count) {
								text.push(' (', section.count, ')')
							}
							text.push(':\n')
							pushCards(section.contents)
							text.push('\n')
						} else {
							if (!section.isConjurations) {
								cardsOnly = cardsOnly.concat(section.contents)
							} else {
								conjurations = section.contents
							}
						}
					}
					if (!this.sortByType) {
						cardsOnly.sort((a, b) => {
							if (a.data.name == b.data.name) return 0
							return a.data.name < b.data.name ? -1 : 1
						})
						pushCards(cardsOnly)
						text.push('\n')
						if (conjurations) {
							text.push('Conjuration Deck:\n')
							pushCards(conjurations)
							text.push('\n')
						}
					}
				}
				if (this.showAttribution) {
					text.push('Created with https://ashes.live')
				}
				return trimEnd(text.join(''))
			}
		},
		methods: {
			close () {
				this.$emit('close')
			},
			selectAll () {
				this.$refs.textarea.focus()
				this.$refs.textarea.select()
				this.$refs.textarea.scrollTop = 0
			}
		}
	}
</script>

