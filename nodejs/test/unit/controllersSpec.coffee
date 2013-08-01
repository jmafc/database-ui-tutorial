'use strict'

describe 'Database UI controllers', ->

  describe 'MyCtrl', ->

    it 'should create a message with specified text', ->
      scope = {}
      ctrl = new MyCtrl(scope)
      console.log(ctrl)
      expect(scope.myMsg).toEqual "Hello, world of Brunch!"
