import os
from statemachine import Action, Classifier, Transition
from statemachine import Event, State
from statemachine import StateMachine, StateMachine_Text

class StateMachine_HTML(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()

    def StateTable1(self):
        the_states = sorted([s.name for s in self.states])
        txt = ['<TABLE BORDER=1>']
        txt += ['<TR>']
        txt += ['<TH><TABLE WIDTH=100%>']
        txt += ['<TR><TD ALIGN="right">Next(&gt;)</TD></TR>']
        txt += ['<TR><TD ALIGN="left">Current(v)</TD></TR>']
        txt += ['</TABLE></TH>']
        for s_next in the_states:
            txt += ['<TH>%s</TH>' % s_next]
        txt += ['</TR>\n']
        for s_curr in the_states:
            txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % s_curr]
            for s_next in the_states:
                txt += ['<TD VALIGN="top"><TABLE>']
                if s_curr == s_next:
                    for block in self.classifiers:
                        if block.source == s_curr:
                            event = block.event
                            action = ',<BR/>'.join(block.actions)
                            txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % event]
                            txt += ['<TD VALIGN="top">%s</TD></TR>' % action]
                for block in self.transitions:
                    if block.source == s_curr and s_next in block.targets:
                        event = block.event
                        action = ',<BR/>'.join(block.actions)
                        txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % event]
                        txt += ['<TD VALIGN="top">%s</TD></TR>' % action]
                txt += ['</TABLE></TD>']
            txt += ['</TR>']
        txt += ['</TABLE>']
        return txt

    def StateTable2(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        txt = ['<TABLE BORDER=1>']
        txt += ['<TR>']
        txt += ['<TH><TABLE WIDTH=100%>']
        txt += ['<TR><TD VALIGN="right">State(&gt;)</TD></TR>']
        txt += ['<TR><TD VALIGN="left">Event(v)</TD></TR>']
        txt += ['</TABLE></TH>']
        for s in the_states:
            txt += ['<TH>%s</TH>' % s]
        txt += ['</TR>\n']
        for e in the_events:
            txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % e]
            for s in the_states:
                txt += ['<TD VALIGN="top"><TABLE>']
                the_blocks = [b for b in self.classifiers + self.transitions if b.source == s]
                for block in the_blocks:
                    if e == block.event:
                        action = ',<BR/>'.join(block.actions)
                        next_state = ''
                        if isinstance(block, Transition):
                            next_state = '<B>' + ',<BR>'.join(block.targets) + '</B>'
                        txt += ['<TR><TD VALIGN="top">%s</TD><TD VALIGN="top">%s</TD></TR>' % (action, next_state)]
                txt += ['</TABLE></TD>']
            txt += ['</TR>']
        txt += ['</TABLE>']
        return txt

    def StateTable3(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        txt = ['<TABLE BORDER=1>\n']
        txt += ['<TR>']
        for t in ['State', 'Event', 'Actions', 'Next']:
            txt += ['<TH>%s</TH>' % t]
        txt += ['</TR>\n']
        for s in the_states:
            for e in the_events:
                the_blocks = [b for b in self.classifiers + self.transitions if b.source == s]
                for block in the_blocks:
                    if e == block.event:
                        txt += ['<TR>']
                        txt += ['<TD VALIGN="top"><B>%s</B></TD>' % s]
                        txt += ['<TD VALIGN="top"><B>%s</B></TD>' % e]
                        action = ',<BR/>'.join(block.actions)
                        txt += ['<TD VALIGN="top">%s</TD>' % action]
                        next_state = ''
                        if isinstance(block, Transition):
                            next_state = '<B>' + ',<BR>'.join(block.targets) + '</B>'
                        else:
                            next_state = s
                        txt += ['<TD VALIGN="top">%s</TD>' % next_state]
                        txt += ['</TR>\n']
        txt += ['</TABLE>\n']
        return txt

    def DotStateMachine(self):
        the_states = sorted([s.name for s in self.states])
        txt = ['digraph G {']
        txt += ['  size="11,8";']
        txt += ['  ratio="expand";']
        txt += ['  rankdir=LR;']
        txt += ['  node [shape=plaintext];']
        txt += ['  labelloc="t";']
        txt += ['  label=<<B>%s</B>>' % self.name]
        txt += ['']
        for state in the_states:
            label = ['<TABLE><TR><TD PORT="f0"><B>']
            label += ['%s' % state]
            label += ['</B></TD></TR>']
            the_blocks = [b for b in self.classifiers if b.source == state]
            the_blocks += [b for b in self.transitions if b.source == state]
            for idx, block in enumerate(the_blocks):
                label += ['<TR><TD><TABLE>']
                label += ['<TR><TD PORT="f%d">' % (idx + 1)]
                label += ['<B>%s</B></TD></TR>' % block.event]
                if len(block.actions) > 0:
                    label += ['<TR><TD>%s</TD></TR>' % '</TD></TR><TR><TD>'.join(block.actions)]
                label += ['</TABLE></TD></TR>']
            label += ['</TABLE>']
            txt += ['  %s[label=<%s>];' % (state, ''.join(label))]
            for idx, block in enumerate(the_blocks):
                if isinstance(block, Transition):
                    for t in block.targets:
                        txt += ['    %s:f%d -> %s:f0;' % (state, idx + 1, t)]
        txt += ['}']
        return txt

    def DotStateMachine2(self):
        the_states = sorted([s.name for s in self.states])
        txt = ['digraph G {']
        txt += ['  size="11,8";']
        txt += ['  ratio="expand";']
        txt += ['  rankdir=LR;']
        txt += ['  node [shape=plaintext];']
        txt += ['  labelloc="t";']
        txt += ['  label=<<B>%s</B>>' % self.name]
        txt += ['']
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'magenta', 'cyan', 'yellow']
        for state in the_states:
            label = ['<TABLE><TR><TD PORT="%s"><B>' % state]
            label += ['%s' % state]
            label += ['</B></TD></TR>']
            the_blocks = [b for b in sorted(self.classifiers) if b.source == state]
            the_blocks += [b for b in sorted(self.transitions) if b.source == state]
            idx = 0
            for block in the_blocks:
                label += ['<TR><TD><TABLE>']
                label += ['<TR><TD PORT="%s">' % block.event]
                label += ['<B>%s</B></TD></TR>' % block.event]
                if len(block.actions) > 0:
                    label += ['<TR><TD>%s</TD></TR>' % '</TD></TR><TR><TD>'.join(block.actions)]
                label += ['</TABLE></TD></TR>']
            label += ['</TABLE>']
            txt += ['  %s[label=<%s>];' % (state, ''.join(label))]
            for block in the_blocks:
                if isinstance(block, Transition):
                    for t in block.targets:
                        txt += ['    %s:%s -> %s:%s;' % (state, block.event, t, t)]
                else:
                    style = 'dir=both,arrowtail=inv,style=dotted,color=%s' % colors[idx]
                    idx += 1
                    if idx >= len(colors):
                        idx = 0
                    for t in block.targets:
                        if t[0] in [b.event for b in the_blocks]:
                            txt += ['    %s:%s -> %s:%s[%s];' % (state, block.event, state, t[0], style)]
        txt += ['}']
        return txt

    def mkSource(self, block):
        if len(block.actions) == 0:
            return block.event
        return block.event + '_source'

    def mkTarget(self, block):
        if len(block.actions) == 0:
            return block.event
        return block.event + '_target'

    def DotStateMachine3(self):
        target_map = {}
        the_states = sorted([s.name for s in self.states])
        txt = ['digraph G {']
        txt += ['  size="11,8";']
        txt += ['  ratio="expand";']
        txt += ['  rankdir=LR;']
        txt += ['  node [shape=plaintext];']
        txt += ['  labelloc="t";']
        txt += ['  label=<<B>%s</B>>' % self.name.upper()]
        txt += ['']
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'magenta', 'cyan', 'yellow']
        for state in the_states:
            label = ['<TABLE>']
            label += ['<TR><TD PORT="%s"><B>%s</B></TD></TR>' % (state, state)]
            the_blocks = [b for b in sorted(self.classifiers) if b.source == state]
            the_blocks += [b for b in sorted(self.transitions) if b.source == state]
            idx = 0
            for block in the_blocks:
                target_text = self.mkTarget(block)
                source_text = self.mkSource(block)
                target_map["%s:%s" % (state, block.event)] = (target_text, source_text)
                label += ['<TR><TD><TABLE>']
                label += ['  <TR><TD PORT="%s"><B>%s</B></TD></TR>' % (self.mkTarget(block), block.event)]
                for (n, a) in enumerate(block.actions):
                    if n < len(block.actions) - 1:
                        label += ['    <TR><TD>%s</TD></TR>' % a]
                    else:
                        label += ['    <TR><TD PORT="%s">%s</TD></TR>' % (self.mkSource(block), a)]
                label += ['</TABLE></TD></TR>']
            label += ['</TABLE>']
            txt += ['  %s[label=<%s>];' % (state, '\n    '.join(label))]
            for block in the_blocks:
                if isinstance(block, Transition):
                    for t in block.targets:
                        txt += ['    %s:%s -> %s:%s;' % (state, self.mkSource(block), t, t)]
                else:
                    style = 'dir=both,arrowtail=inv,style=dotted,color=%s' % colors[idx]
                    idx += 1
                    if idx >= len(colors):
                        idx = 0
                    for t in block.targets:
                        for b in [b for b in the_blocks if t[0] == b.event]:
                            txt += ['    %s:%s -> %s:%s[%s];' % (state, self.mkSource(block), state, self.mkTarget(b), style)]
        txt += ['}']
        return txt

    def Generate(self, dest_file, SourceData, Reformatted):
        TABLE_START = '<TABLE BORDER=0 ALIGN="center">\n'
        TABLE_END = '</TABLE>\n'
        HDR_FMT = '<P style="page-break-before: always" ALIGN="center">%s</P>\n'
        basename = os.path.basename(dest_file)

        text = open("%s.html" % dest_file, "w")
        text.write('<HTML>\n')
        text.write('<TITLE>Finite State Machine %s</TITLE>\n' % dest_file)

        text.write('<P ALIGN="center">%s</P>\n' % 'Source Code')

        text.write(TABLE_START)
        text.write('<TR><TD ALIGN="left">\n')
        text.write('<TABLE BORDER=1 ALIGN="center">\n')
        text.write('<TR><TH ALIGN="center">What you wrote</TH><TH ALIGN="center">What I saw</TH></TR>\n')
        text.write('<TR><TD ALIGN="left" VALIGN="top">\n')
        text.write('<PRE>\n' + '\n'.join(SourceData) + '\n</PRE>\n')
        text.write('</TD><TD ALIGN="left">\n')
        # Insert the Reformatted State Machine text
        text.write('<PRE>\n' + '\n'.join(Reformatted) + '\n</PRE>\n')
        text.write('</TD></TR></TABLE>\n')
        text.write('</TD></TR>\n')

        text.write(TABLE_END + HDR_FMT % 'State Diagram' + TABLE_START)

        text.write('<TR><TD ALIGN="center">\n')
        text.write('<img src="%s.svg" alt="%s.svg"/>\n' % (basename, basename))
        text.write('</TD></TR>\n')
        text.write(TABLE_END + HDR_FMT % 'State Diagram' + TABLE_START)
        text.write('<TR><TD ALIGN="center">\n')
        text.write('<img src="%s.png" alt="%s.png"/>\n' % (basename, basename))
        text.write('</TD></TR>\n')

        text.write(TABLE_END + HDR_FMT % 'State Table 1' + TABLE_START)

        text.write('<TR><TD ALIGN="center">\n')
        txt = self.StateTable1()
        text.write('\n'.join(txt))
        text.write('</TD></TR>\n')

        text.write(TABLE_END + HDR_FMT % 'State Table 2' + TABLE_START)

        text.write('<TR><TD ALIGN="center">\n')
        txt = self.StateTable2()
        text.write('\n'.join(txt))
        text.write('</TD></TR>\n')

        text.write(TABLE_END + HDR_FMT % 'State Table 3' + TABLE_START)

        text.write('<TR><TD ALIGN="center">\n')
        txt = self.StateTable3()
        text.write('\n'.join(txt))
        text.write('</TD></TR>\n')

        text.write('</TABLE>\n')
        text.write('</HTML>\n')
        text.close()
        pdf_cmd = 'wkhtmltopdf -T 10mm -B 10mm %s.html %s.pdf' % (dest_file, dest_file)
        print pdf_cmd
        #os.system(pdf_cmd)

        
