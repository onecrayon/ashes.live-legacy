<template>
	<span class="ashes-500-points">
		<span v-if="costQty1 !== null" :class="{active: cardQty >= 1}">{{ costQty1 }}</span
		><span v-if="costQty2 !== null">
			\ <span :class="{active: cardQty >= 2}">{{ costQty2 }}</span
		></span
		><span v-if="costQty3 !== null">
			\ <span :class="{active: cardQty >= 3}">{{ costQty3 }}</span
		></span>
		<span v-if="comboTooltip" class="tooltip" :class="{'always-active': hasActiveCombo}" :title="comboTooltip">
			<i class="fa fa-exclamation-circle"></i>
		</span>
	</span>
</template>

<script>
	import {initTooltips, teardownTooltips} from 'app/utils'
	import {includes} from 'lodash'

	export default {
		props: ['card'],
		mounted: initTooltips,
		updated: function () {
			teardownTooltips.call(this)
			initTooltips.call(this)
		},
		beforeDestroy: teardownTooltips,
		computed: {
			cardData () {
				if (this.card.data) return this.card.data
				return this.card
			},
			cardQty () {
				if (this.card.count) return this.card.count
				const count = this.$store.state.deck.cards[this.cardData.id]
				return !count ? 0 : count
			},
			hasActiveCombo () {
				const combo_ids = this.$store.getters.activeComboIds
				if (includes(combo_ids, this.cardData.id)) return true
				// Need to check for combo-ing with a particular card type
				const costs = this.cardData.ashes_500_costs
				if (!costs || costs.length <= 1) return false
				for (const cost of costs) {
					if (cost.combo_card_type) {
						return !!this.cardCountByType(cost.combo_card_type)
					}
				}
				return false
			},
			cardIds () {
				const cardIds = Object.keys(this.$store.state.deck.cards).map(str => parseInt(str))
				cardIds.push(this.$store.state.deck.phoenixborn)
				return cardIds
			},
			comboTooltip () {
				const costs = this.cardData.ashes_500_costs
				if ((!costs || costs.length <= 1) && !this.cardData.ashes_500_combos) {
					return null
				}
				let statements = []
				for (let cost of costs) {
					if (cost.combo_card_type) {
						statements.push('+' + cost.qty_1 + ' for each ' + cost.combo_card_type + ' card')
					}
					if (!cost.combo_card_id) continue
					let comboCard = this.$store.state.cardManager.cardById(cost.combo_card_id)
					if (cost.qty_2 === null) {
						statements.push('+' + cost.qty_1 + ' with ' + comboCard.name)
					} else if (cost.qty_1 === cost.qty_2 && cost.qty_1 === cost.qty_3) {
						statements.push('+' + cost.qty_1 + ' per copy with ' + comboCard.name)
					}
				}
				if (!this.cardData.ashes_500_combos) return statements.join('; ')
				for (let comboId of this.cardData.ashes_500_combos) {
					let comboedCard = this.$store.state.cardManager.cardById(comboId)
					for (let cost of comboedCard.ashes_500_costs) {
						if (!cost.combo_card_id || cost.combo_card_id !== this.cardData.id) continue
						if (cost.qty_2 === null) {
							statements.push('+' + cost.qty_1 + ' with ' + comboedCard.name)
						} else if (cost.qty_1 === cost.qty_2 && cost.qty_1 === cost.qty_3) {
							statements.push('+' + cost.qty_1 + ' per copy of ' + comboedCard.name)
						}
					}
				}
				return statements.join('; ')
			},
			costQty1 () {
				if (!this.cardData.ashes_500_costs) return null
				let total = 0
				for (let cost of this.cardData.ashes_500_costs) {
					if (!cost.qty_1 || (cost.combo_card_id && !includes(this.cardIds, cost.combo_card_id))) {
						continue
					}
					if (cost.combo_card_type) {
						total += (cost.qty_1 * this.cardCountByType(cost.combo_card_type))
					} else {
						total += cost.qty_1
					}
				}
				return total
			},
			costQty2 () {
				if (!this.cardData.ashes_500_costs || this.cardData.type == 'Phoenixborn') return null
				let total = 0
				for (let cost of this.cardData.ashes_500_costs) {
					if (!cost.qty_2 || (cost.combo_card_id && !includes(this.cardIds, cost.combo_card_id)) || cost.combo_card_type) {
						continue
					}
					total += cost.qty_2
				}
				return total
			},
			costQty3 () {
				if (!this.cardData.ashes_500_costs || this.cardData.type == 'Phoenixborn') return null
				let total = 0
				for (let cost of this.cardData.ashes_500_costs) {
					if (!cost.qty_3 || (cost.combo_card_id && !includes(this.cardIds, cost.combo_card_id)) || cost.combo_card_type) {
						continue
					}
					total += cost.qty_3
				}
				return total
			}
		},
		methods: {
			cardCountByType (type) {
				const cards = this.$store.getters.allCards
				let count = 0
				for (const card of cards) {
					if (card.type === type) {
						count += 1
					}
				}
				return count
			}
		}
	}
</script>
