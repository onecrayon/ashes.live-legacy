<template>
	<span class="ashes-500-points">
		<span v-if="costQty1 !== null" class="active">{{ costQty1 }}</span
		><span v-if="costQty2 !== null">
			\ <span :class="{active: card.count >= 2}">{{ costQty2 }}</span
		></span
		><span v-if="costQty3 !== null">
			\ <span :class="{active: card.count >= 3}">{{ costQty3 }}</span
		></span>
		<span v-if="comboTooltip" class="tooltip" :class="{active: hasActiveCombo}" :title="comboTooltip">
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
			hasActiveCombo () {
				const combo_ids = this.$store.getters.activeComboIds
				return includes(combo_ids, this.card.data.id)
			},
			cardIds () {
				return Object.keys(this.$store.state.deck.cards).map(str => parseInt(str))
			},
			comboTooltip () {
				const costs = this.card.data.ashes_500_costs
				if ((!costs || costs.length <= 1) && !this.card.data.ashes_500_combos) {
					return null
				}
				let statements = []
				for (let cost of costs) {
					if (!cost.combo_card_id) continue
					let comboCard = this.$store.state.cardManager.cardById(cost.combo_card_id)
					if (cost.qty_2 === null) {
						statements.push('+' + cost.qty_1 + ' with ' + comboCard.name)
					} else if (cost.qty_1 === cost.qty_2 && cost.qty_1 === cost.qty_3) {
						statements.push('+' + cost.qty_1 + ' per copy with ' + comboCard.name)
					}
				}
				if (!this.card.data.ashes_500_combos) return statements.join('; ')
				for (let comboId of this.card.data.ashes_500_combos) {
					let comboedCard = this.$store.state.cardManager.cardById(comboId)
					for (let cost of comboedCard.ashes_500_costs) {
						if (!cost.combo_card_id || cost.combo_card_id !== this.card.data.id) continue
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
				if (!this.card.data.ashes_500_costs) return null
				let total = 0
				for (let cost of this.card.data.ashes_500_costs) {
					if (!cost.qty_1 || (cost.combo_card_id && !includes(this.cardIds, cost.combo_card_id))) {
						continue
					}
					total += cost.qty_1
				}
				return total
			},
			costQty2 () {
				if (!this.card.data.ashes_500_costs) return null
				let total = 0
				for (let cost of this.card.data.ashes_500_costs) {
					if (!cost.qty_2 || (cost.combo_card_id && !includes(this.cardIds, cost.combo_card_id))) {
						continue
					}
					total += cost.qty_2
				}
				return total
			},
			costQty3 () {
				if (!this.card.data.ashes_500_costs) return null
				let total = 0
				for (let cost of this.card.data.ashes_500_costs) {
					if (!cost.qty_3 || (cost.combo_card_id && !includes(this.cardIds, cost.combo_card_id))) {
						continue
					}
					total += cost.qty_3
				}
				return total
			}
		}
	}
</script>
