<template>
	<div class="textarea-helpers responsive-cols">
		<div class="btn-group col">
			<button class="btn btn-small" type="button" title="Bold"
				data-cursor-prefix="**" data-cursor-suffix="**"
			><i class="fa fa-bold"></i></button
			><button class="btn btn-small" type="button" title="Italic"
				data-cursor-prefix="*" data-cursor-suffix="*"
			><i class="fa fa-italic"></i></button>
		</div>
		<div class="btn-group col">
			<button class="btn btn-small" type="button" title="List"
				data-line-prefix="* "><i class="fa fa-list-ul"></i></button
			><button class="btn btn-small" type="button" title="Quote"
				data-line-prefix="> "><i class="fa fa-quote-left"></i></button>
		</div>
		<div class="btn-group col-flex">
			<button class="btn btn-small" type="button" title="Wrap with [[ ]]"
				data-cursor-prefix="[[" data-cursor-suffix="]]"
			><strong>[[&hellip;]]</strong></button>
		</div>
	</div>
</template>

<script>
import {initTextareaHelpers} from 'app/utils'

export default {
	mounted () {
		initTextareaHelpers([this.$el])
	}
}
</script>

