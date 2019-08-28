<template>
	<div class="btn-group">
		<button @click="toggleDiceLogic"
			class="btn btn-all" :class="{active: isDiceLogicActive }"
			:disabled="isDisabled" :title="diceLogicTooltip">{{ diceLogicText }}:</button
		><button @click="toggleDie('basic')"
			class="btn phg-basic-magic" :class="{active: isDieActive('basic') }"
			:disabled="isBasicDisabled || isDisabled" title="Basic Magic"></button
		><button v-for="dieType of diceList" :key="dieType"
			@click="toggleDie(dieType)" :title="capitalize(dieType) + ' Magic'"
			class="btn" :class="[isDieActive(dieType) ? 'active' : '', 'phg-' + dieType + '-power']"
			:disabled="!isShowingRelease(dieType) || isDisabled"></button>
	</div>
</template>

<script>
	import {capitalize, includes} from 'lodash'
	import {globals} from 'app/utils'
	
	export default {
		computed: {
			isDisabled () {
				return this.$store.state.isDisabled
			},
			diceList () {
				return globals.diceData
			},
			diceLogicText () {
				return this.isDiceLogicActive ? 'All' : 'Any'
			},
			diceLogicTooltip () {
				if (this.isDiceLogicActive) {
					return 'Showing cards that require ALL selected magic types'
				}
				return 'Showing cards that require ANY selected magic type'
			},
			isDiceLogicActive () {
				return this.$store.state.options.diceLogic === 'and'
			},
			isBasicDisabled () {
				return this.$store.state.options.diceLogic === 'and'
			}
		},
		methods: {
			capitalize,
			toggleDiceLogic () {
				this.$store.commit('toggleDiceLogic')
				this.$store.dispatch('filterCards')
			},
			toggleDie (die) {
				this.$store.commit('toggleDieFilter', die)
				this.$store.dispatch('filterCards')
			},
			isDieActive (die) {
				return includes(this.$store.state.options.dice || [], die)
			},
			isShowingRelease (dieType) {
				// TODO: update this to handle Time dice
				return true
			}
		}
	}
</script>

