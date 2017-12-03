<template>
	<div class="filters">
		<div class="responsive-cols main-filters">
			<dice-filter class="col"></dice-filter>
			<text-filter class="col-flex"></text-filter>
		</div>
		<div class="secondary-filters responsive-cols">
			<div class="btn-group col">
				<button @click="toggleCardType('Ally')"
					class="btn btn-small" :class="{active: isTypeActive('Ally')}"
					><i class="fa" :class="typeToFontAwesome('Ally')"></i> <span class="full-display-only">Ally</span></button
				><button @click="toggleCardType('Action Spell')"
					class="btn btn-small" :class="{active: isTypeActive('Action Spell')}"
					><i class="fa" :class="typeToFontAwesome('Action Spell')"></i> <span class="full-display-only">Action</span></button
				><button @click="toggleCardType('Reaction Spell')"
					class="btn btn-small" :class="{active: isTypeActive('Reaction Spell')}"
					><i class="fa" :class="typeToFontAwesome('Reaction Spell')"></i> <span class="full-display-only">Reaction</span></button
				><button @click="toggleCardType('Alteration Spell')"
					class="btn btn-small" :class="{active: isTypeActive('Alteration Spell')}"
					><i class="fa" :class="typeToFontAwesome('Alteration Spell')"></i> <span class="full-display-only">Alteration</span></button
				><button @click="toggleCardType('Ready Spell')"
					class="btn btn-small" :class="{active: isTypeActive('Ready Spell')}"
					><i class="fa" :class="typeToFontAwesome('Ready Spell')"></i> <span class="full-display-only">Ready</span></button
				><button @click="toggleCardType('summon')"
					class="btn btn-small" :class="{active: isTypeActive('summon')}"
					><i class="fa" :class="typeToFontAwesome('summon')"></i> <span class="full-display-only">Summon</span></button
				>
			</div>
			<release-filter class="col"></release-filter>
		</div>
		<div class="responsive-cols listing-controls">
			<sort-filter class="col"></sort-filter>
			<div class="btn-group col">
				<!--<button @click="setListType('grid')"
					class="btn btn-small" :class="{active: isListType('grid')}" disabled
					><i class="fa fa-th" title="Grid"></i></button
				>--><button @click="setListType('list')"
					class="btn btn-small" :class="{active: isListType('list')}"
					><i class="fa fa-th-list" title="List"></i></button
				><button @click="setListType('table')"
					class="btn btn-small" :class="{active: isListType('table')}"
					><i class="fa fa-bars" title="Simple List"></i></button
				>
			</div>
		</div>
	</div>
</template>

<script>
	import DiceFilter from './dice.vue'
	import ReleaseFilter from './releases.vue'
	import SortFilter from './sort.vue'
	import TextFilter from './text.vue'
	import {includes} from 'lodash'
	import {typeToFontAwesome} from 'app/utils'

	export default {
		components: {
			'dice-filter': DiceFilter,
			'release-filter': ReleaseFilter,
			'sort-filter': SortFilter,
			'text-filter': TextFilter
		},
		methods: {
			typeToFontAwesome,
			toggleCardType (typeName) {
				this.$store.commit('toggleTypeFilter', typeName)
				this.$store.commit('filterCards')
			},
			setListType (listType) {
				this.$store.commit('setListType', listType)
			},
			isTypeActive (typeName) {
				return includes(this.$store.state.options.types || [], typeName)
			},
			isListType (listType) {
				return this.$store.state.options.listType === listType
			}
		}
	}
</script>
