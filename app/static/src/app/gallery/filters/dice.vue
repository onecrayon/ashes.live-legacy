<template>
	<div class="btn-group">
		<button @click="toggleDiceLogic"
			class="btn btn-all" :class="{active: isDiceLogicActive }"
			:disabled="isDisabled">{{ diceLogicText }}:</button
		><button @click="toggleDie('basic')"
			class="btn phg-basic-magic" :class="{active: isDieActive('basic') }"
			:disabled="isBasicDisabled || isDisabled" title="Basic"></button
		><button v-for="dieType of diceList" :key="dieType"
			@click="toggleDie(dieType)" :title="capitalize(dieType)"
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
				return this.$store.state.options.diceLogic === 'or' ? 'Any' : 'All'
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
				let releasesKey = null
				if (dieType === 'divine' || dieType === 'sympathy') {
					releasesKey = 'expansions'
				}
				if (!releasesKey) return true
				return includes(this.$store.state.options.releases, releasesKey)
			}
		}
	}
</script>

