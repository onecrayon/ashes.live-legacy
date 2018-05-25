<template>
	<span class="ashes-500-points">
		<span v-if="costQty1 !== null" class="active">{{ costQty1 }}</span
		><span v-if="costQty2 !== null">
			\ <span :class="{active: card.count >= 2}">{{ costQty2 }}</span
		></span
		><span v-if="costQty3 !== null">
			\ <span :class="{active: card.count >= 3}">{{ costQty3 }}</span
		></span>
		<span v-if="card.data.ashes_500_costs.length > 1 || card.data.ashes_500_combos" :class="{active: hasActiveCombo}">
			<!-- TODO: add title and tooltip logic to show the combo details on tap/hover -->
			<!-- TODO: add active class if any combo is added to the score -->
			<i class="fa fa-exclamation-circle"></i>
		</span>
	</span>
</template>

<script>
	import {initCardTooltips, teardownTooltips} from 'app/utils'
	import {includes} from 'lodash'

	export default {
		props: ['card'],
		// mounted: function () {
		// 	initCardTooltips.call(this, this.$el)
		// },
		// updated: function () {
		// 	teardownTooltips.call(this)
		// 	initCardTooltips.call(this, this.$el)
		// },
		// beforeDestroy: teardownTooltips,
		computed: {
			hasActiveCombo () {
				const combo_ids = this.$store.getters.activeComboIds
				return includes(combo_ids, this.card.data.id)
			},
			cardIds () {
				return Object.keys(this.$store.state.deck.cards).map(str => parseInt(str))
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
