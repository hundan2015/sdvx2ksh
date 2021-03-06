#!/usr/bin/env python
# coding:utf-8
from __future__ import unicode_literals
import wx
import wx.richtext
import sys, time
import pafy
from copy import copy
from sdvx2ksh import *
import time
import subprocess

class myConsole(wx.richtext.RichTextCtrl):
	def __init__(self, *args, **kwargs):
		wx.richtext.RichTextCtrl.__init__(self,style=wx.TE_MULTILINE|\
		                                wx.TE_READONLY|\
		                                wx.HSCROLL|\
		                                wx.VSCROLL, *args, **kwargs)
		self.SetBackgroundColour('black')
		self.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
		self.cyan = wx.Colour(0,255,255,255)
		self.red = wx.Colour(255,0,0,255)
		self.BeginTextColour(self.cyan)
		self.Bind(wx.EVT_TEXT, self.OnText)

		sys.stdout = copy(self)
		sys.stderr = copy(self)
		sys.stdout.write = self.stdout
		sys.stderr.write = self.stderr
		print "console init is finished..."

	def stdout(self, txt):
		self.WriteText(txt)

	def stderr(self, txt):
		self.BeginTextColour(self.red)
		self.WriteText(txt)
		self.BeginTextColour(self.cyan)

	def OnText(self, event):
		wx.Yield()
		self.ScrollPages(1)

	def flush(self):
		value = self.Value
#		if 'Rate' in v.split('\n')[-4]:
		indexs = [i for i,v in enumerate(value) if v == '\n']
		self.Remove(indexs[-2], indexs[-1])
		self.SetInsertionPoint(len(value))

class myFrame(wx.Frame):
	def __init__(self):
		self.scores = dict()
		wx.Frame.__init__(self, None, -1, 'sdvx2ksh_ver1.1β')
		self.SetSize((600,700))
		self.panel_root = wx.Panel(self, size=self.GetSize())
		#self.panel.SetBackgroundColour('white')
		font = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

		self.panel_url = wx.Panel(self.panel_root)

		self.text = wx.StaticText(self.panel_url, -1, 'url')
		self.text.SetFont(font)

		self.urlctrl = wx.TextCtrl(self.panel_url, -1)
		self.urlctrl.SetFont(font)

		self.button = wx.Button(self.panel_url, -1, 'run', size=(40,30))
		self.button.SetFont(font)
		self.button.Bind(wx.EVT_BUTTON, self.run)

		self.panel_log = wx.Panel(self.panel_root)
		self.log = myConsole(self.panel_log, -1, pos=(0,50))

		layout_url = wx.BoxSizer(wx.HORIZONTAL)
		layout_url.Add(self.text, proportion=0)
		layout_url.Add(self.urlctrl, proportion=1)
		layout_url.Add(self.button, proportion=0)
                self.panel_url.SetSizer(layout_url)

		layout_log = wx.BoxSizer(wx.VERTICAL)
		layout_log.Add(self.log, proportion=1, flag=wx.GROW)
		self.panel_log.SetSizer(layout_log)

		layout_root = wx.BoxSizer(wx.VERTICAL)
		layout_root.Add(self.panel_url, proportion=0, flag=wx.GROW)
		layout_root.Add(self.panel_log, proportion=1, flag=wx.GROW)
		self.panel_root.SetSizer(layout_root)

		print "frame init is finished..."

#		self.timer = wx.Timer(self)
#		self.Bind(wx.EVT_TIMER, self.OnTimer)
#		self.timer.Start(500)
#
#	def OnTimer(self, event):
#		wx.Yield()

	def run(self, event):
		url = self.urlctrl.GetValue()
		self.button.Disable()
		if url not in self.scores:
			self.scores[url] = Score(url)
		score = self.scores[url]
		try:
			print 'now exec sdvx2ksh...'

			score.setCorrectUrl()
			score.setHeader()
			safefilename = score.header['title']
			safefilename = safefilename.encode('sjis','replace').decode('sjis')
			safefilename = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '', safefilename)
			home = os.getcwd()
			path = 'kshootmania/songs/sdvx2ksh/' + safefilename
			try:
				os.makedirs(path)
			except WindowsError:
				print "既にフォルダが作られています"
			try:
				os.chdir(path)
				if os.path.exists('jacket_' + score._d + '.jpg'):
					print "一度譜面を作っているようです、もう一度実行したいときは  "\
					+ path + "  以下のファイルを削除してください。"
					raise Exception
				score.getImage('jacket').save('jacket_' + score._d + '.jpg')
				score.dl_music()
				adjustWave('fx_' + score._d + '.wav','nofx_' + score._d + '.wav')
				with open(score._d + '.ksh', 'w') as f:
					f.write((score.getHeader() + parseScore(score)).encode('sjis','replace'))

				print "全てのプロセスが正常終了しました。エディターを起動します。"
				subprocess.Popen(
					(os.path.abspath('../../../editor.exe') + ' ' +
					 os.path.abspath(score._d+'.ksh')).encode('sjis'))

			finally:
				os.chdir(home)

		finally:
#			self.urlctrl.SetValue('')
			self.button.Enable()


if __name__ == '__main__':
	app = wx.App()
	frame = myFrame()
	frame.Show()
	print 'now app is in mainloop...'
	app.MainLoop()
	sys.stdout = sys.__stdout__
